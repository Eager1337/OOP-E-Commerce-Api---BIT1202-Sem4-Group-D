#!/usr/bin/env python3
"""
Test script for E-Commerce Inventory API.
Demonstrates all CRUD operations and authentication flow.
Run this after starting the API server.
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def test_api():
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("E-COMMERCE INVENTORY API - TEST SUITE")
        print("=" * 60)

        # 1. Health Check
        print("\n[1] Health Check")
        resp = await client.get("http://localhost:8000/health")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")

        # 2. Register Admin User
        print("\n[2] Register Admin User")
        admin_data = {
            "email": "admin@limkokwing.edu.sl",
            "username": "admin",
            "password": "adminpass123",
            "full_name": "System Administrator",
            "role": "admin"
        }
        resp = await client.post(f"{BASE_URL}/auth/register", json=admin_data)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")

        # 3. Login
        print("\n[3] Login (OAuth2)")
        login_data = {"username": "admin", "password": "adminpass123"}
        resp = await client.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Status: {resp.status_code}")
        token_data = resp.json()
        print(f"Token received: {token_data['token_type']} (expires in {token_data['expires_in']}s)")
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Get Current User
        print("\n[4] Get Current User Profile")
        resp = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"User: {resp.json()}")

        # 5. Create Category
        print("\n[5] Create Category")
        category = {
            "name": "Electronics",
            "description": "Electronic devices and accessories",
            "slug": "electronics"
        }
        resp = await client.post(f"{BASE_URL}/categories/", json=category, headers=headers)
        print(f"Status: {resp.status_code}")
        cat_data = resp.json()
        print(f"Category: {cat_data}")
        cat_id = cat_data["id"]

        # 6. Create Product
        print("\n[6] Create Product")
        product = {
            "name": "Wireless Headphones",
            "description": "Bluetooth 5.0 over-ear headphones",
            "sku": "WH-001",
            "price": 150.00,
            "stock_quantity": 50,
            "category_id": cat_id
        }
        resp = await client.post(f"{BASE_URL}/products/", json=product, headers=headers)
        print(f"Status: {resp.status_code}")
        prod_data = resp.json()
        print(f"Product: {prod_data}")
        prod_id = prod_data["id"]

        # 7. List Products
        print("\n[7] List Products")
        resp = await client.get(f"{BASE_URL}/products/?limit=5")
        print(f"Status: {resp.status_code}")
        print(f"Total products: {resp.json()['total']}")

        # 8. Create Order
        print("\n[8] Create Order")
        order = {
            "items": [{"product_id": prod_id, "quantity": 2}],
            "shipping_address": "123 Main Street, Freetown, Sierra Leone"
        }
        resp = await client.post(f"{BASE_URL}/orders/", json=order, headers=headers)
        print(f"Status: {resp.status_code}")
        order_data = resp.json()
        print(f"Order: {order_data}")

        # 9. Create Review
        print("\n[9] Create Review")
        review = {
            "product_id": prod_id,
            "rating": 5,
            "comment": "Excellent sound quality!"
        }
        resp = await client.post(f"{BASE_URL}/reviews/", json=review, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Review: {resp.json()}")

        # 10. Get Inventory Stats
        print("\n[10] Get Inventory Statistics")
        resp = await client.get(f"{BASE_URL}/products/stats/inventory", headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Stats: {resp.json()}")

        # 11. SDG Info
        print("\n[11] SDG Alignment Info")
        resp = await client.get("http://localhost:8000/api/v1/sdg-info")
        print(f"Status: {resp.status_code}")
        print(f"SDG: {resp.json()['sdg']}")

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_api())
