import asyncio
import httpx
import time
import sys

# Basic stress test script
# Usage: python tests/stress_test.py <url> <api_key>

async def send_requests(url, api_key, count=20):
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(count):
            tasks.append(client.post(
                f"{url}/scans",
                json={"target": f"example{i}.com"},
                headers={"X-API-Key": api_key}
            ))
        
        start = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end = time.time()
        
        print(f"Sent {count} requests in {end - start:.2f} seconds")
        
        success = 0
        rate_limited = 0
        errors = 0
        
        for r in responses:
            if isinstance(r, Exception):
                errors += 1
                continue
            if r.status_code == 200:
                data = r.json()
                if "id" in data and data["status"] == "pending":
                    success += 1
                else:
                    print(f"Unexpected response format: {data}")
                    errors += 1
            elif r.status_code == 429:
                rate_limited += 1
            else:
                print(f"Unexpected status: {r.status_code}")
                errors += 1
                
        print(f"Success: {success}")
        print(f"Rate Limited: {rate_limited}")
        print(f"Errors: {errors}")

if __name__ == "__main__":
    target_url = "http://localhost:8000"
    target_key = "gloaks-secret-123"
    
    print(f"Stress testing {target_url} with key {target_key}")
    try:
        asyncio.run(send_requests(target_url, target_key))
    except KeyboardInterrupt:
        pass
