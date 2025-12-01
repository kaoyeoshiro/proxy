"""
Proxy simples para TJ-MS
Deploy no Fly.io com datacenter em São Paulo
"""

from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

TJ_URL = "https://esaj.tjms.jus.br/mniws/servico-intercomunicacao-2.2.2/intercomunicacao"

@app.get("/")
async def health():
    return {"status": "ok", "service": "tjms-proxy"}

@app.post("/")
async def proxy_soap(request: Request):
    """Repassa requisição SOAP para o TJ-MS"""
    body = await request.body()
    
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(
                TJ_URL,
                content=body,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": ""
                }
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type="text/xml"
            )
        except httpx.TimeoutException:
            return Response(
                content="<error>Timeout ao conectar com TJ-MS</error>",
                status_code=504,
                media_type="text/xml"
            )
        except Exception as e:
            return Response(
                content=f"<error>{str(e)}</error>",
                status_code=500,
                media_type="text/xml"
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
