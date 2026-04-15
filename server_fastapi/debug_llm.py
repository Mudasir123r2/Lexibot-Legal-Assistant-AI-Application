import pathlib
import re

file_path = pathlib.Path(r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\services\llm_service.py')
content = file_path.read_text(encoding='utf-8')

# Let's change the error handling in generate_response to print the actual error
content = content.replace('error_str = str(api_error)', 'error_str = str(api_error)\n                    logger.error(f"LLM API ERROR: {error_str}")\n                    print("LLM API ERROR:", error_str)')

file_path.write_text(content, encoding='utf-8')
