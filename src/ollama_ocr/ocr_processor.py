import json
from typing import Dict, Any, List, Union, Optional
import os
import base64
import requests
from tqdm import tqdm
import concurrent.futures
from pathlib import Path
import cv2
import pymupdf 
import numpy as np
from threading import Lock
import tiktoken

class OCRProcessor:
    # Preços por 1M tokens (input/output) - atualizados conforme a API
    PRICING = {
        "openai": {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.150, "output": 0.600},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        },
        "gemini": {
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-2.0-flash-exp": {"input": 0.00, "output": 0.00},
        },
        "ollama": {
            "default": {"input": 0.00, "output": 0.00}  # Ollama é local e gratuito
        }
    }
    
    # Taxa de câmbio USD para BRL (atualizar conforme necessário)
    USD_TO_BRL = 6.10
    
    def __init__(self, model_name: str = "llama3.2-vision:11b", 
                 base_url: str = "http://localhost:11434/api/generate",
                 max_workers: int = 1,
                 api_provider: str = "ollama",
                 api_key: Optional[str] = None,
                 progress_callback: Optional[callable] = None):
        
        self.model_name = model_name
        self.base_url = base_url
        self.max_workers = max_workers
        self.api_provider = api_provider.lower()
        self.api_key = api_key
        self.progress_callback = progress_callback
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
        # Initialize tokenizer for OpenAI models
        if self.api_provider == "openai":
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model_name)
            except:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
        else:
            self.tokenizer = None
        
        # Validate API key for external providers
        if self.api_provider in ["openai", "gemini"] and not self.api_key:
            raise ValueError(f"API key is required for {self.api_provider}")
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Aproximação: ~4 caracteres por token
            return len(text) // 4
    
    def _estimate_image_tokens(self, image_path: str) -> int:
        """Estimate token count for image based on resolution"""
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                return 0
            height, width = img.shape[:2]
            
            # OpenAI vision pricing model
            # Base tokens + tiles based on image size
            if self.api_provider == "openai":
                # Images are resized to fit within 2048x2048
                # Each 512x512 tile costs ~170 tokens
                tiles = ((width // 512) + 1) * ((height // 512) + 1)
                return 85 + (tiles * 170)
            elif self.api_provider == "gemini":
                # Gemini charges ~258 tokens per image
                return 258
            else:
                # Ollama local - estimate based on image size
                return (width * height) // 1000
        except:
            return 500  # Default estimate
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on tokens and model pricing"""
        if self.api_provider == "ollama":
            return 0.0
        
        pricing = None
        if self.api_provider == "openai":
            # Find matching pricing
            for model_key in self.PRICING["openai"]:
                if model_key in self.model_name:
                    pricing = self.PRICING["openai"][model_key]
                    break
            if not pricing:
                pricing = self.PRICING["openai"]["gpt-4o"]  # Default
        elif self.api_provider == "gemini":
            for model_key in self.PRICING["gemini"]:
                if model_key in self.model_name:
                    pricing = self.PRICING["gemini"][model_key]
                    break
            if not pricing:
                pricing = self.PRICING["gemini"]["gemini-1.5-flash"]  # Default
        
        if pricing:
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            return input_cost + output_cost
        return 0.0
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "estimated_cost_usd": self.total_cost,
            "estimated_cost_brl": self.total_cost * self.USD_TO_BRL,
            "usd_to_brl_rate": self.USD_TO_BRL,
            "model": self.model_name,
            "provider": self.api_provider
        }
    
    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def _encode_image(self, image_path: str) -> str:
        """Convert image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def _call_openai_vision(self, image_base64: str, prompt: str, image_path: str = None) -> str:
        """Call OpenAI Vision API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        
        # Track tokens
        usage = result.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += self._calculate_cost(input_tokens, output_tokens)
        
        return result["choices"][0]["message"]["content"]
    
    def _call_gemini_vision(self, image_base64: str, prompt: str, image_path: str = None) -> str:
        """Call Google Gemini Vision API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Track tokens (Gemini provides usage metadata)
        usage = result.get("usageMetadata", {})
        input_tokens = usage.get("promptTokenCount", 0)
        output_tokens = usage.get("candidatesTokenCount", 0)
        
        # If tokens not provided, estimate them
        if input_tokens == 0:
            input_tokens = self._estimate_tokens(prompt)
            if image_path:
                input_tokens += self._estimate_image_tokens(image_path)
        
        response_text = result["candidates"][0]["content"]["parts"][0]["text"]
        if output_tokens == 0:
            output_tokens = self._estimate_tokens(response_text)
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += self._calculate_cost(input_tokens, output_tokens)
        
        return response_text
    
    def _call_vision_api(self, image_base64: str, prompt: str, image_path: str = None) -> str:
        """Route to appropriate vision API based on provider"""
        if self.api_provider == "openai":
            return self._call_openai_vision(image_base64, prompt, image_path)
        elif self.api_provider == "gemini":
            return self._call_gemini_vision(image_base64, prompt, image_path)
        else:  # ollama
            # Estimate tokens for Ollama (no cost, but still track usage)
            input_tokens = self._estimate_tokens(prompt)
            if image_path:
                input_tokens += self._estimate_image_tokens(image_path)
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "images": [image_base64]
            }
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            result_text = response.json().get("response", "")
            
            output_tokens = self._estimate_tokens(result_text)
            
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            # Ollama is free
            
            return result_text

    def _pdf_to_images(self, pdf_path: str) -> List[str]:
        """
        Convert each page of a PDF to an image using pymupdf.
        Saves each page as a temporary image.
        Returns a list of image paths.
        """
        try:
            doc = pymupdf.open(pdf_path)
            image_paths = []
            for page_num in range(doc.page_count):
                page = doc[page_num]
                pix = page.get_pixmap()  # Render page to an image
                temp_path = f"{pdf_path}_page{page_num}.png"  # Define output image path
                pix.save(temp_path)  # Save the image
                image_paths.append(temp_path)
            doc.close()
            return image_paths
        except Exception as e:
            raise ValueError(f"Could not convert PDF to images: {e}")

    def _preprocess_image(self, image_path: str, language: str = "en") -> str:
        """
        Preprocess image before OCR:
        - Convert PDF to image if needed (using pymupdf)
        - Language-specific preprocessing (if applicable)
        - Enhance contrast
        - Reduce noise
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image at {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced)

        # Language-specific thresholding
        if language.lower() in ["japanese", "chinese", "zh", "korean"]:
            # For some CJK and similar languages adaptive thresholding may work better
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2)
            thresh = cv2.bitwise_not(thresh)
        else:
            # Default: Otsu thresholding
            thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            thresh = cv2.bitwise_not(thresh)

        # Save preprocessed image
        preprocessed_path = f"{image_path}_preprocessed.jpg"
        cv2.imwrite(preprocessed_path, thresh)

        return preprocessed_path

    def process_image(self, image_path: str, format_type: str = "markdown", preprocess: bool = True, 
                      custom_prompt: str = None, language: str = "en") -> str:
        """
        Process an image (or PDF) and extract text in the specified format

        Args:
            image_path: Path to the image file or PDF file
            format_type: One of ["markdown", "text", "json", "structured", "key_value","custom"]
            preprocess: Whether to apply image preprocessing
            custom_prompt: If provided, this prompt overrides the default based on format_type
            language: Language code to apply language specific OCR preprocessing
        """
        try:
            # If the input is a PDF, process all pages
            if image_path.lower().endswith('.pdf'):
                image_pages = self._pdf_to_images(image_path)
                responses = []
                total_pages = len(image_pages)
                
                for idx, page_file in enumerate(image_pages):
                    # Report progress for PDF pages
                    if self.progress_callback:
                        self.progress_callback(idx, total_pages, f"Processando página {idx + 1} de {total_pages}")
                    
                    # Process each page with preprocessing if enabled
                    if preprocess:
                        preprocessed_path = self._preprocess_image(page_file, language)
                    else:
                        preprocessed_path = page_file

                    image_base64 = self._encode_image(preprocessed_path)

                    if custom_prompt and custom_prompt.strip():
                        prompt = custom_prompt
                    else:
                        prompts = {
                            "markdown": f"""Extract all text content from this image in {language} **exactly as it appears**, without modification, summarization, or omission.
                                Format the output in markdown:
                                - Use headers (#, ##, ###) **only if they appear in the image**
                                - Preserve original lists (-, *, numbered lists) as they are
                                - Maintain all text formatting (bold, italics, underlines) exactly as seen
                                - **Do not add, interpret, or restructure any content**
                            """,
                            "text": f"""Extract all visible text from this image in {language} **without any changes**.
                                - **Do not summarize, paraphrase, or infer missing text.**
                                - Retain all spacing, punctuation, and formatting exactly as in the image.
                                - If text is unclear or partially visible, extract as much as possible without guessing.
                                - **Include all text, even if it seems irrelevant or repeated.** 
                                """,


                           "json": f"""Extract all text from this image in {language} and format it as JSON, **strictly preserving** the structure.
                                - **Do not summarize, add, or modify any text.**
                                - Maintain hierarchical sections and subsections as they appear.
                                - Use keys that reflect the document's actual structure (e.g., "title", "body", "footer").
                                - Include all text, even if fragmented, blurry, or unclear.
                                """,


                            "structured": f"""Extract all text from this image in {language}, **ensuring complete structural accuracy**:
                                - Identify and format tables **without altering content**.
                                - Preserve list structures (bulleted, numbered) **exactly as shown**.
                                - Maintain all section headings, indents, and alignments.
                                - **Do not add, infer, or restructure the content in any way.**
                                """,


                           "key_value": f"""Extract all key-value pairs from this image in {language} **exactly as they appear**:
                                - Identify and extract labels and their corresponding values without modification.
                                - Maintain the exact wording, punctuation, and order.
                                - Format each pair as 'key: value' **only if clearly structured that way in the image**.
                                - **Do not infer missing values or add any extra text.**
                                """,

                            "table": f"""Extract all tabular data from this image in {language} **exactly as it appears**, without modification, summarization, or omission.
                                - **Preserve the table structure** (rows, columns, headers) as closely as possible.
                                - **Do not add missing values or infer content**—if a cell is empty, leave it empty.
                                - Maintain all numerical, textual, and special character formatting.
                                - If the table contains merged cells, indicate them clearly without altering their meaning.
                                - Output the table in a structured format such as Markdown, CSV, or JSON, based on the intended use.
                                """,


                        }
                        prompt = prompts.get(format_type, prompts["text"])

                    # Make the API call
                    res = self._call_vision_api(image_base64, prompt, preprocessed_path)
                    # Prefix result with page number
                    responses.append(f"Page {idx + 1}:\n{res}")

                    # Clean up temporary files
                    if preprocess and preprocessed_path.endswith('_preprocessed.jpg'):
                        os.remove(preprocessed_path)
                    if page_file.endswith('.png'):
                        os.remove(page_file)

                final_result = "\n".join(responses)
                if format_type == "json":
                    try:
                        json_data = json.loads(final_result)
                        return json.dumps(json_data, indent=2)
                    except json.JSONDecodeError:
                        return final_result
                return final_result

            # Process non-PDF images as before.
            processed_path = image_path
            if preprocess:
                processed_path = self._preprocess_image(image_path, language)

            image_base64 = self._encode_image(processed_path)

            if custom_prompt and custom_prompt.strip():
                prompt = custom_prompt
            else:
                prompts = {
                            "markdown": f"""Extract all text content from this image in {language} **exactly as it appears**, without modification, summarization, or omission.
                                Format the output in markdown:
                                - Use headers (#, ##, ###) **only if they appear in the image**
                                - Preserve original lists (-, *, numbered lists) as they are
                                - Maintain all text formatting (bold, italics, underlines) exactly as seen
                                - **Do not add, interpret, or restructure any content**
                            """,
                            "text": f"""Extract all visible text from this image in {language} **without any changes**.
                                - **Do not summarize, paraphrase, or infer missing text.**
                                - Retain all spacing, punctuation, and formatting exactly as in the image.
                                - If text is unclear or partially visible, extract as much as possible without guessing.
                                - **Include all text, even if it seems irrelevant or repeated.** 
                                """,


                           "json": f"""Extract all text from this image in {language} and format it as JSON, **strictly preserving** the structure.
                                - **Do not summarize, add, or modify any text.**
                                - Maintain hierarchical sections and subsections as they appear.
                                - Use keys that reflect the document's actual structure (e.g., "title", "body", "footer").
                                - Include all text, even if fragmented, blurry, or unclear.
                                """,


                            "structured": f"""Extract all text from this image in {language}, **ensuring complete structural accuracy**:
                                - Identify and format tables **without altering content**.
                                - Preserve list structures (bulleted, numbered) **exactly as shown**.
                                - Maintain all section headings, indents, and alignments.
                                - **Do not add, infer, or restructure the content in any way.**
                                """,


                           "key_value": f"""Extract all key-value pairs from this image in {language} **exactly as they appear**:
                                - Identify and extract labels and their corresponding values without modification.
                                - Maintain the exact wording, punctuation, and order.
                                - Format each pair as 'key: value' **only if clearly structured that way in the image**.
                                - **Do not infer missing values or add any extra text.**
                                """,

                            "table": f"""Extract all tabular data from this image in {language} **exactly as it appears**, without modification, summarization, or omission.
                                - **Preserve the table structure** (rows, columns, headers) as closely as possible.
                                - **Do not add missing values or infer content**—if a cell is empty, leave it empty.
                                - Maintain all numerical, textual, and special character formatting.
                                - If the table contains merged cells, indicate them clearly without altering their meaning.
                                - Output the table in a structured format such as Markdown, CSV, or JSON, based on the intended use.
                                """,
                }
                prompt = prompts.get(format_type, prompts["text"])

            result = self._call_vision_api(image_base64, prompt, processed_path)
            
            # Clean up temporary files
            if processed_path.endswith(('_preprocessed.jpg', '_temp.jpg')):
                os.remove(processed_path)

            if format_type == "json":
                try:
                    json_data = json.loads(result)
                    return json.dumps(json_data, indent=2)
                except json.JSONDecodeError:
                    return result

            return result
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def process_batch(
        self,
        input_path: Union[str, List[str]],
        format_type: str = "markdown",
        recursive: bool = False,
        preprocess: bool = True,
        custom_prompt: str = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process multiple images in batch
        
        Args:
            input_path: Path to directory or list of image paths
            format_type: Output format type
            recursive: Whether to search directories recursively
            preprocess: Whether to apply image preprocessing
            custom_prompt: If provided, this prompt overrides the default for each image
            language: Language code to apply language specific OCR preprocessing
            
        Returns:
            Dictionary with results and statistics
        """
        # Collect all image paths
        image_paths = []
        if isinstance(input_path, str):
            base_path = Path(input_path)
            if base_path.is_dir():
                pattern = '**/*' if recursive else '*'
                for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.tiff']:
                    image_paths.extend(base_path.glob(f'{pattern}{ext}'))
            else:
                image_paths = [base_path]
        else:
            image_paths = [Path(p) for p in input_path]

        results = {}
        errors = {}
        completed = 0
        total = len(image_paths)

        # Process images in parallel with progress bar
        with tqdm(total=total, desc="Processing images", disable=self.progress_callback is not None) as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_path = {
                    executor.submit(self.process_image, str(path), format_type, preprocess, custom_prompt, language): path
                    for path in image_paths
                }
                
                for future in concurrent.futures.as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        results[str(path)] = future.result()
                    except Exception as e:
                        errors[str(path)] = str(e)
                    
                    completed += 1
                    if self.progress_callback:
                        self.progress_callback(completed, total, f"Processando arquivo {completed} de {total}")
                    pbar.update(1)

        return {
            "results": results,
            "errors": errors,
            "statistics": {
                "total": len(image_paths),
                "successful": len(results),
                "failed": len(errors)
            }
        }