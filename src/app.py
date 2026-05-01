"""
Exercise 01 — Node Registry API

Implement a FastAPI application with the following endpoints:

GET    /health          → health check with DB status
POST   /api/nodes       → register a new node
GET    /api/nodes       → list all nodes
GET    /api/nodes/{name} → get a node by name
PUT    /api/nodes/{name} → update a node
DELETE /api/nodes/{name} → soft-delete a node (set status=inactive)

See README.md for full specification.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from . import models, schemas, database

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Node Registry API")

@app.get("/health")
def health_check(db: Session = Depends(database.get_db)):
    try:
        # Check DB connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    active_nodes_count = db.query(models.Node).filter(models.Node.status == "active").count()

    return {
        "status": "ok",
        "db": db_status,
        "nodes_count": active_nodes_count
    }

@app.post("/api/nodes", response_model=schemas.NodeResponse, status_code=status.HTTP_201_CREATED)
def register_node(node: schemas.NodeCreate, db: Session = Depends(database.get_db)):
    db_node = db.query(models.Node).filter(models.Node.name == node.name).first()
    if db_node:
        raise HTTPException(status_code=409, detail="Node already exists")

    new_node = models.Node(**node.model_dump())
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node

@app.get("/api/nodes", response_model=List[schemas.NodeResponse])
def list_nodes(db: Session = Depends(database.get_db)):
    return db.query(models.Node).all()

@app.get("/api/nodes/{name}", response_model=schemas.NodeResponse)
def get_node(name: str, db: Session = Depends(database.get_db)):
    node = db.query(models.Node).filter(models.Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@app.put("/api/nodes/{name}", response_model=schemas.NodeResponse)
def update_node(name: str, node_update: schemas.NodeUpdate, db: Session = Depends(database.get_db)):
    db_node = db.query(models.Node).filter(models.Node.name == name).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")

    update_data = node_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_node, key, value)

    db.commit()
    db.refresh(db_node)
    return db_node

@app.delete("/api/nodes/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(name: str, db: Session = Depends(database.get_db)):
    db_node = db.query(models.Node).filter(models.Node.name == name).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")

    db_node.status = "inactive"
    db.commit()
    return None
