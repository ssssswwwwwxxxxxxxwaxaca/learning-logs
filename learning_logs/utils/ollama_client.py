import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    """与本地部署的Ollama模型交互的客户端"""
    
    def __init__(self, model_name="llama3"):
        self.base_url = getattr(settings, 'OLLAMA_API_URL', 'http://localhost:11434')
        self.model = model_name
        
    def generate_response(self, prompt, system_prompt=None, max_tokens=1000, temperature=0.7):
        """向Ollama发送请求并获取响应"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return f"Error: Unable to get response from AI model (Status code: {response.status_code})"
        except Exception as e:
            logger.error(f"Exception when calling Ollama API: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_topic_summary(self, topic_text, entries_text):
        """为学习主题生成摘要"""
        prompt = f"""
        Create a concise summary of this learning topic:
        
        Topic: {topic_text}
        
        Content:
        {entries_text}
        
        Provide a summary that captures the key points and main ideas.
        """
        
        system_prompt = "You are an educational assistant helping students summarize their learning materials."
        
        return self.generate_response(prompt, system_prompt)
        
    def generate_quiz(self, topic_text, entries_text, num_questions=5):
        """根据学习内容生成测验题"""
        prompt = f"""
        Based on the following learning material, generate {num_questions} quiz questions with answers.
        Include a mix of question types (multiple choice, true/false, short answer).
        
        Topic: {topic_text}
        
        Content:
        {entries_text}
        
        Format each question with its answer clearly marked.
        """
        
        system_prompt = "You are an educational quiz generator. Create challenging but fair questions based on the learning material."
        
        return self.generate_response(prompt, system_prompt)
    
    def get_learning_recommendations(self, topic_text, entries_text):
        """为学习主题提供进一步学习的建议"""
        prompt = f"""
        Based on this learning material, suggest additional resources, next topics to study, 
        or activities to deepen understanding.
        
        Topic: {topic_text}
        
        Content:
        {entries_text}
        
        Provide 3-5 specific recommendations that would help someone advance their knowledge in this area.
        """
        
        system_prompt = "You are an expert educational advisor helping students plan their learning path."
        
        return self.generate_response(prompt, system_prompt)
    
    def answer_question(self, question, context):
        """根据学习内容回答问题"""
        prompt = f"""
        Question: {question}
        
        Context:
        {context}
        
        Answer the question based on the provided context. If the answer cannot be determined from the context, say so.
        """
        
        system_prompt = "You are a helpful AI tutor assisting with questions about learning materials."
        
        return self.generate_response(prompt, system_prompt)