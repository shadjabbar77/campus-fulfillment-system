from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.optimization import router as optimization_router

app = FastAPI(title="CampusFlow")

app.include_router(optimization_router)


@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CampusFlow</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                margin: 0;
                padding: 40px;
                color: #1f2937;
            }
            .container {
                max-width: 960px;
                margin: auto;
                background: white;
                padding: 36px;
                border-radius: 18px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            }
            h1 {
                font-size: 42px;
                margin-bottom: 8px;
            }
            .subtitle {
                font-size: 18px;
                color: #4b5563;
                margin-bottom: 28px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin: 28px 0;
            }
            .card {
                background: #f9fafb;
                padding: 18px;
                border-radius: 14px;
                border: 1px solid #e5e7eb;
            }
            .metric {
                font-size: 28px;
                font-weight: bold;
                color: #111827;
            }
            .label {
                font-size: 13px;
                color: #6b7280;
                margin-top: 6px;
            }
            .buttons {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin-top: 28px;
            }
            a {
                text-decoration: none;
                background: #111827;
                color: white;
                padding: 12px 16px;
                border-radius: 10px;
                font-weight: bold;
            }
            a.secondary {
                background: #e5e7eb;
                color: #111827;
            }
            .section {
                margin-top: 32px;
            }
            code {
                background: #f3f4f6;
                padding: 3px 6px;
                border-radius: 6px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CampusFlow</h1>
            <div class="subtitle">
                Real-Time Campus Logistics Optimization Engine
            </div>

            <p>
                CampusFlow simulates campus package fulfillment using shortest-path routing,
                capacity-aware locker assignment, express-priority scheduling, and benchmarked
                fulfillment metrics.
            </p>

            <div class="grid">
                <div class="card">
                    <div class="metric">1000</div>
                    <div class="label">Orders Simulated</div>
                </div>
                <div class="card">
                    <div class="metric">81.43%</div>
                    <div class="label">Distance Reduced</div>
                </div>
                <div class="card">
                    <div class="metric">61.31%</div>
                    <div class="label">Delivery Time Reduced</div>
                </div>
                <div class="card">
                    <div class="metric">33.33</div>
                    <div class="label">Express SLA Gain</div>
                </div>
            </div>

            <div class="section">
                <h2>Core Engineering Features</h2>
                <ul>
                    <li>Dijkstra shortest-path routing across a weighted campus graph</li>
                    <li>Capacity-aware locker assignment with package-size constraints</li>
                    <li>Heap-based express priority scheduling</li>
                    <li>FastAPI optimization endpoints</li>
                    <li>Redis/RQ async worker pipeline</li>
                    <li>Pytest algorithm and API test suite</li>
                </ul>
            </div>

            <div class="buttons">
                <a href="/docs">Open API Demo</a>
                <a class="secondary" href="/optimization/health">Health Check</a>
                <a class="secondary" href="/optimization/campus">Campus Data</a>
                <a class="secondary" href="/optimization/metrics">Benchmark Metrics</a>
            </div>

            <div class="section">
                <p>
                    Try the interactive API at <code>/docs</code>, then run
                    <code>POST /optimization/orders</code> with a sample package order.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
