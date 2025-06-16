from transformers import AutoTokenizer, AutoModelForCausalLM
from optimum.onnxruntime import ORTModelForCausalLM
import torch
from .config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMHandler:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    async def load_model(self):
        """加载模型和分词器"""
        try:
            logger.info("开始加载模型...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_NAME,
                trust_remote_code=True,
                cache_dir=settings.MODEL_CACHE_DIR
            )

            if settings.USE_ONNX:
                logger.info("使用ONNX优化版本...")
                self.model = ORTModelForCausalLM.from_pretrained(
                    settings.MODEL_NAME,
                    cache_dir=settings.MODEL_CACHE_DIR,
                    use_int8=settings.USE_INT8
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.MODEL_NAME,
                    trust_remote_code=True,
                    cache_dir=settings.MODEL_CACHE_DIR,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float32
                )

            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            logger.info("模型加载完成")
            return True
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            return False

    async def generate_response(self, prompt: str, max_length: int = None, temperature: float = None):
        """生成回复"""
        try:
            if not self.model or not self.tokenizer:
                raise RuntimeError("模型未加载")

            max_length = max_length or settings.MAX_LENGTH
            temperature = temperature or settings.DEFAULT_TEMPERATURE

            # 为DEEPSEEK模型格式化输入
            formatted_prompt = f"<｜begin▁of▁sentence｜>{prompt}"
            
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=min(max_length - inputs['input_ids'].shape[1], 512),  # 限制新生成的token数量
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id if self.tokenizer.pad_token_id else self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )

            # 只返回新生成的部分
            generated_text = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            return generated_text.strip()

        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}")
            raise

llm_handler = LLMHandler() 