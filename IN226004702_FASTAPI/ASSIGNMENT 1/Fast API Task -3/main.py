from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

# ------------------ DATA ------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]


# ------------------ HELPER ------------------
def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# ------------------ MODELS ------------------
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


# ------------------ GET ALL ------------------
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# ------------------ Q5 (IMPORTANT: ABOVE ID ROUTE) ------------------
@app.get("/products/audit")
def product_audit():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    total_value = sum(p["price"] * 10 for p in in_stock)
    expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_names": [p["name"] for p in out_stock],
        "total_stock_value": total_value,
        "most_expensive": {
            "name": expensive["name"],
            "price": expensive["price"]
        }
    }


# ------------------ BONUS ------------------
@app.put("/products/discount")
def discount_products(
    category: str = Query(...),
    discount_percent: int = Query(..., ge=1, le=99)
):
    updated = []

    for p in products:
        if p["category"] == category:
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"message": f"No products found in category: {category}"}

    return {
        "message": f"{discount_percent}% discount applied",
        "updated_count": len(updated),
        "products": updated
    }


# ------------------ GET BY ID ------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        return {"error": "Product not found"}
    return product


# ------------------ POST ------------------
@app.post("/products", status_code=201)
def add_product(data: NewProduct, response: Response):

    for p in products:
        if p["name"].lower() == data.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_product = data.dict()
    new_product["id"] = new_id

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


# ------------------ PUT ------------------
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: int = None,
    in_stock: bool = None
):
    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}


# ------------------ DELETE ------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}


@app.get("/products/audit")
def product_audit():

    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }


@app.put("/products/discount")
def bulk_discount(category: str, discount_percent: int):

    updated = []

    for p in products:
        if p["category"] == category:
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"message": f"No products found in category: {category}"}

    return {
        "message": f"{discount_percent}% discount applied",
        "updated_count": len(updated),
        "updated_products": updated
    }