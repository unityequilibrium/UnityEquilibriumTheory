import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


class UETResponseComposer:
    def compose(
        self,
        prompt: str,
        equilibrium_data: Dict[str, Any],
        task_type: str = "chat",
        recent_episodes: Optional[List[Dict[str, Any]]] = None,
        procedure_hint: str = "",
    ) -> str:
        api_key = os.getenv("OPENROUTER_API_KEY", "")

        if not equilibrium_data["equilibrium_found"]:
            return "ไม่พบข้อมูลที่เสถียรพอในระบบ (Entropy สูงเกินไป) กรุณาเพิ่มข้อมูล Source เพื่อ 'เทรน' AI ก่อนทำการวิเคราะห์"

        top_chunks = equilibrium_data.get("top_chunks", [])
        if not top_chunks:
            chunk = equilibrium_data["best_chunk"]
            top_chunks = [chunk] if chunk else []
        source_text = "\n\n---\n\n".join(c["text"] for c in top_chunks)
        work = equilibrium_data["work_computed"]
        score = equilibrium_data["resonance_score"]

        if not api_key:
            prefix = "ระบบค้นพบจุดสมดุล"
            if task_type == "calculation":
                prefix = "ระบบประเมินเส้นทางการคำนวณและพบจุดสมดุล"
            return f"{prefix} (Resonance: {score:.4f}) จากฐานข้อมูล:\n\n\"{source_text}\"\n\n*ใช้ Work ไป {work:.4f} Ω ในการค้นหา (ยังไม่ได้ต่อ API LLM)*"

        try:
            episode_context = ""
            if recent_episodes:
                episode_lines = []
                for episode in recent_episodes[-3:]:
                    episode_lines.append(
                        f"- [{episode.get('task_type', 'chat')}] Q: {episode.get('prompt', '')} | A: {episode.get('response', '')[:120]}"
                    )
                episode_context = "\n".join(episode_lines)

            system_content = "คุณคือ UET Communicator หน้าที่ของคุณคือรับข้อมูลดิบจากสมการ UET แล้วนำมาเรียบเรียงตอบคำถามผู้ใช้ให้เป็นภาษาไทยที่อ่านง่าย เป็นธรรมชาติ และตอบตรงประเด็น โดยต้องอ้างอิงจากข้อมูลดิบที่ได้รับเท่านั้น ห้ามคิดคำตอบเองเด็ดขาด ถ้าข้อมูลไม่เกี่ยวให้บอกไปตรงๆ"
            if procedure_hint:
                system_content = f"{system_content}\n\nแนวปฏิบัติของงานนี้: {procedure_hint}"

            user_content = f"ประเภทงาน: {task_type}\nคำถามจากผู้ใช้: {prompt}\n\nข้อมูลที่ได้จาก UET Engine: {source_text}"
            if episode_context:
                user_content = f"{user_content}\n\nบริบทตอนก่อนหน้า:\n{episode_context}"

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "z-ai/glm-4.7-flash",
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_content
                        },
                        {
                            "role": "user",
                            "content": user_content
                        }
                    ]
                }
            )

            res_json = response.json()
            msg = res_json["choices"][0]["message"]
            llm_text = msg.get("content") or msg.get("reasoning", "")

            return f"{llm_text}\n\n---\n*⚡ คำนวณผ่าน UET Engine (Resonance: {score:.4f} | Work: {work:.4f} Ω)*"
        except Exception as e:
            print(f"LLM API Error: {e}")
            return f"ระบบค้นพบจุดสมดุล (Resonance: {score:.4f}) จากฐานข้อมูล:\n\n\"{source_text}\"\n\n*ใช้ Work ไป {work:.4f} Ω ในการค้นหา (API เรียบเรียงภาษาขัดข้อง)*"
