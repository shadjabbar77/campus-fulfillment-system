from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


def create_test_client(tmp_path):
    test_db_path = tmp_path / "test_packages.db"
    test_database_url = f"sqlite:///{test_db_path}"

    test_engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_create_order(tmp_path):
    client = create_test_client(tmp_path)

    response = client.post(
        "/orders",
        data={
            "student_name": "Amy",
            "student_email": "amy@example.com",
            "priority": "STANDARD",
        },
    )

    assert response.status_code == 200

    orders = client.get("/api/orders").json()

    assert len(orders) == 1
    assert orders[0]["student_name"] == "Amy"
    assert orders[0]["status"] == "PENDING"
    assert orders[0]["priority"] == "STANDARD"


def test_express_order_gets_first_locker(tmp_path):
    client = create_test_client(tmp_path)

    client.post("/orders", data={
        "student_name": "Amy",
        "student_email": "amy@example.com",
        "priority": "STANDARD",
    })

    client.post("/orders", data={
        "student_name": "Jose",
        "student_email": "jose@example.com",
        "priority": "EXPRESS",
    })

    client.post("/orders", data={
        "student_name": "Ashley",
        "student_email": "ashley@example.com",
        "priority": "STANDARD",
    })

    client.post("/process")

    orders = client.get("/api/orders").json()

    jose = next(order for order in orders if order["student_name"] == "Jose")
    amy = next(order for order in orders if order["student_name"] == "Amy")
    ashley = next(order for order in orders if order["student_name"] == "Ashley")

    assert jose["priority"] == "EXPRESS"
    assert jose["locker_number"] == "A1"
    assert amy["locker_number"] == "A2"
    assert ashley["locker_number"] == "A3"


def test_pickup_updates_status(tmp_path):
    client = create_test_client(tmp_path)

    client.post("/orders", data={
        "student_name": "Jose",
        "student_email": "jose@example.com",
        "priority": "EXPRESS",
    })

    client.post("/process")

    order = client.get("/api/orders").json()[0]

    client.post(f"/pickup/{order['id']}")

    updated_order = client.get("/api/orders").json()[0]

    assert updated_order["status"] == "PICKED_UP"
    assert updated_order["locker_number"] is None


def test_stats_endpoint(tmp_path):
    client = create_test_client(tmp_path)

    client.post("/orders", data={
        "student_name": "Amy",
        "student_email": "amy@example.com",
        "priority": "STANDARD",
    })

    stats = client.get("/api/stats").json()

    assert stats["pending"] == 1
    assert stats["standard"] == 1
    assert stats["express"] == 0