from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from typing import List

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./kizzylord.portfolio"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models for SQLAlchemy ORM
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)

class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)

class ContactInfo(Base):
    __tablename__ = "contact_info"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    address = Column(String)

Base.metadata.create_all(bind=engine)

# Pydantic Schemas for Request and Response models
class ProjectBase(BaseModel):
    title: str
    description: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True

class BlogPostBase(BaseModel):
    title: str
    content: str

class BlogPostCreate(BlogPostBase):
    pass

class BlogPost(BlogPostBase):
    id: int

    class Config:
        from_attributes = True

class ContactInfoBase(BaseModel):
    email: str
    phone: str
    address: str

class ContactInfoCreate(ContactInfoBase):
    pass

class ContactInfo(ContactInfoBase):
    id: int

    class Config:
        from_attributes = True

# CRUD operations for the database
def create_project(db: Session, title: str, description: str):
    db_project = Project(title=title, description=description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Project).offset(skip).limit(limit).all()

def update_project(db: Session, project_id: int, title: str, description: str):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        project.title = title
        project.description = description
        db.commit()
        db.refresh(project)
    return project

def delete_project(db: Session, project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
    return project

def create_blog_post(db: Session, title: str, content: str):
    db_blog_post = BlogPost(title=title, content=content)
    db.add(db_blog_post)
    db.commit()
    db.refresh(db_blog_post)
    return db_blog_post

def get_blog_post(db: Session, blog_post_id: int):
    return db.query(BlogPost).filter(BlogPost.id == blog_post_id).first()

def get_blog_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(BlogPost).offset(skip).limit(limit).all()

def update_blog_post(db: Session, blog_post_id: int, title: str, content: str):
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_post_id).first()
    if blog_post:
        blog_post.title = title
        blog_post.content = content
        db.commit()
        db.refresh(blog_post)
    return blog_post

def delete_blog_post(db: Session, blog_post_id: int):
    blog_post = db.query(BlogPost).filter(BlogPost.id == blog_post_id).first()
    if blog_post:
        db.delete(blog_post)
        db.commit()
    return blog_post

def create_contact_info(db: Session, email: str, phone: str, address: str):
    db_contact_info = ContactInfo(email=email, phone=phone, address=address)
    db.add(db_contact_info)
    db.commit()
    db.refresh(db_contact_info)
    return db_contact_info

def get_contact_info(db: Session, contact_info_id: int):
    return db.query(ContactInfo).filter(ContactInfo.id == contact_info_id).first()

def get_contact_infos(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ContactInfo).offset(skip).limit(limit).all()

def update_contact_info(db: Session, contact_info_id: int, email: str, phone: str, address: str):
    contact_info = db.query(ContactInfo).filter(ContactInfo.id == contact_info_id).first()
    if contact_info:
        contact_info.email = email
        contact_info.phone = phone
        contact_info.address = address
        db.commit()
        db.refresh(contact_info)
    return contact_info

def delete_contact_info(db: Session, contact_info_id: int):
    contact_info = db.query(ContactInfo).filter(ContactInfo.id == contact_info_id).first()
    if contact_info:
        db.delete(contact_info)
        db.commit()
    return contact_info

# FastAPI application instance
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints

# Project Endpoints

@app.post("/projects/", response_model=Project, tags=["Projects"])
def create_project_endpoint(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    **Create a new project**

    **Parameters:**
    - `project`: ProjectCreate - A JSON object containing `title` and `description` of the project

    **Returns:**
    - The newly created project as a JSON object with `id`, `title`, and `description`
    """
    return create_project(db=db, title=project.title, description=project.description)

@app.get("/projects/{project_id}", response_model=Project, tags=["Projects"])
def read_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    """
    **Get a single project by ID**

    **Parameters:**
    - `project_id`: int - The ID of the project

    **Returns:**
    - The project details as a JSON object with `id`, `title`, and `description`

    **Raises:**
    - `HTTPException` with status code 404 if the project is not found
    """
    db_project = get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.get("/projects/", response_model=List[Project], tags=["Projects"])
def read_projects_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    **Get all projects**

    **Parameters:**
    - `skip`: int (optional) - Number of projects to skip
    - `limit`: int (optional) - Maximum number of projects to return

    **Returns:**
    - A list of projects as JSON objects
    """
    projects = get_projects(db, skip=skip, limit=limit)
    return projects

@app.put("/projects/{project_id}", response_model=Project, tags=["Projects"])
def update_project_endpoint(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    """
    **Update a project by ID**

    **Parameters:**
    - `project_id`: int - The ID of the project
    - `project`: ProjectCreate - A JSON object containing the updated `title` and `description`

    **Returns:**
    - The updated project as a JSON object

    **Raises:**
    - `HTTPException` with status code 404 if the project is not found
    """
    db_project = update_project(db, project_id=project_id, title=project.title, description=project.description)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.delete("/projects/{project_id}", response_model=Project, tags=["Projects"])
def delete_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    """
    **Delete a project by ID**

    **Parameters:**
    - `project_id`: int - The ID of the project

    **Returns:**
    - The deleted project as a JSON object

    **Raises:**
    - `HTTPException` with status code 404 if the project is not found
    """
    db_project = delete_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project
print()
#Project API endpoint sumarry 

#POST /projects/: Create a new project.
#GET /projects/{project_id}: Retrieve a specific project by ID.
#GET /projects/: List all projects with optional pagination.
#PUT /projects/{project_id}: Update a specific project by ID.
#DELETE /projects/{project_id}: Delete a specific project by ID.

# BlogPost Endpoints

@app.post("/blog_posts/", response_model=BlogPost, tags=["Blog Posts"])
def create_blog_post_endpoint(blog_post: BlogPostCreate, db: Session = Depends(get_db)):
    """
    **Create a new blog post**

    **Parameters:**
    - `blog_post`: BlogPostCreate - A JSON object containing `title` and `content`

    **Returns:**
    - The newly created blog post as a JSON object with `id`, `title`, and `content`
    """
    return create_blog_post(db=db, title=blog_post.title, content=blog_post.content)

@app.get("/blog_posts/{blog_post_id}", response_model=BlogPost, tags=["Blog Posts"])
def read_blog_post_endpoint(blog_post_id: int, db: Session = Depends(get_db)):
    """
    **Get a single blog post by ID**

    **Parameters:**
    - `blog_post_id`: int - The ID of the blog post

    **Returns:**
    - The blog post details as a JSON object with `id`, `title`, and `content`

    **Raises:**
    - `HTTPException` with status code 404 if the blog post is not found
    """
    db_blog_post = get_blog_post(db, blog_post_id=blog_post_id)
    if db_blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return db_blog_post

@app.get("/blog_posts/", response_model=List[BlogPost], tags=["Blog Posts"])
def read_blog_posts_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    **Get all blog posts**

    **Parameters:**
    - `skip`: int (optional) - Number of blog posts to skip
    - `limit`: int (optional) - Maximum number of blog posts to return

    **Returns:**
    - A list of blog posts as JSON objects
    """
    blog_posts = get_blog_posts(db, skip=skip, limit=limit)
    return blog_posts

@app.put("/blog_posts/{blog_post_id}", response_model=BlogPost, tags=["Blog Posts"])
def update_blog_post_endpoint(blog_post_id: int, blog_post: BlogPostCreate, db: Session = Depends(get_db)):
    """
    **Update a blog post by ID**

    **Parameters:**
    - `blog_post_id`: int - The ID of the blog post
    - `blog_post`: BlogPostCreate - A JSON object containing the updated `title` and `content`

    **Returns:**
    - The updated blog post as a JSON object

    **Raises:**
    - `HTTPException` with status code 404 if the blog post is not found
    """
    db_blog_post = update_blog_post(db, blog_post_id=blog_post_id, title=blog_post.title, content=blog_post.content)
    if db_blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return db_blog_post

@app.delete("/blog_posts/{blog_post_id}", response_model=BlogPost, tags=["Blog Posts"])
def delete_blog_post_endpoint(blog_post_id: int, db: Session = Depends(get_db)):
    """
    **Delete a blog post by ID**

    **Parameters:**
    - `blog_post_id`: int - The ID of the blog post

    **Returns:**
    - The deleted blog post as a JSON object

    **Raises:**
    - `HTTPException` with status code 404 if the blog post is not found
    """
    db_blog_post = delete_blog_post(db, blog_post_id=blog_post_id)
    if db_blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return db_blog_post
#Blogpost API endpoint Summary
#POST /blog_posts/: Create a new blog post.
#GET /blog_posts/{blog_post_id}: Retrieve a specific blog post by ID.
#GET /blog_posts/: List all blog posts with optional pagination.
#PUT /blog_posts/{blog_post_id}: Update a specific blog post by ID.
#DELETE /blog_posts/{blog_post_id}: Delete a specific blog post by ID

# ContactInfo Endpoints

@app.post("/contact_info/", response_model=ContactInfo, tags=["Contact Info"])
def create_contact_info_endpoint(contact_info: ContactInfoCreate, db: Session = Depends(get_db)):
    """
    **Create new contact information**

    **Parameters:**
    - `contact_info`: ContactInfoCreate - A JSON object containing `email`, `phone`, and `address`

    **Returns:**
    - The newly created contact info as a JSON object with `id`, `email`, `phone`, and `address`
    """
    return create_contact_info(db=db, email=contact_info.email, phone=contact_info.phone, address=contact_info.address)

@app.get("/contact_info/{contact_info_id}", response_model=ContactInfo, tags=["Contact Info"])
def read_contact_info_endpoint(contact_info_id: int, db: Session = Depends(get_db)):
    """
    **Get contact information by ID**

    **Parameters:**
    - `contact_info_id`: int - The ID of the contact info

    **Returns:**
    - The contact info as a JSON object with `id`, `email`, `phone`, and `address`

    **Raises:**
    - `HTTPException` with status code 404 if the contact info is not found
    """
    db_contact_info = get_contact_info(db, contact_info_id=contact_info_id)
    if db_contact_info is None:
        raise HTTPException(status_code=404, detail="Contact info not found")
    return db_contact_info

@app.get("/contact_info/", response_model=List[ContactInfo], tags=["Contact Info"])
def read_contact_infos_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    **Get all contact information**

    **Parameters:**
    - `skip`: int (optional) - Number of contact info entries to skip
    - `limit`: int (optional) - Maximum number of contact info entries to return

    **Returns:**
    - A list of contact info as JSON objects
    """
    contact_infos = get_contact_infos(db, skip=skip, limit=limit)
    return contact_infos

@app.put("/contact_info/{contact_info_id}", response_model=ContactInfo, tags=["Contact Info"])
def update_contact_info_endpoint(contact_info_id: int, contact_info: ContactInfoCreate, db: Session = Depends(get_db)):
    """
    **Update contact information by ID**

    **Parameters:**
    - `contact_info_id`: int - The ID of the contact info
    - `contact_info`: ContactInfoCreate - A JSON object containing the updated `email`, `phone`, and `address`

    **Returns:**
    - The updated contact info as a JSON object

    **Raises:**
    - `HTTPException` with status code 404 if the contact info is not found
    """
    db_contact_info = update_contact_info(db, contact_info_id=contact_info_id, email=contact_info.email, phone=contact_info.phone, address=contact_info.address)
    if db_contact_info is None:
        raise HTTPException(status_code=404, detail="Contact info not found")
    return db_contact_info

@app.delete("/contact_info/{contact_info_id}", response_model=ContactInfo, tags=["Contact Info"])
def delete_contact_info_endpoint(contact_info_id: int, db: Session = Depends(get_db)):
    """
    **Delete contact information by ID**

    **Parameters:**
    - `contact_info_id`: int - The ID of the contact info

    **Returns:**
    - The deleted contact info as a JSON object

    **Raises:**
    - `HTTPException` with status code 404 if the contact info is not found
    """
    db_contact_info = delete_contact_info(db, contact_info_id=contact_info_id)
    if db_contact_info is None:
        raise HTTPException(status_code=404, detail="Contact info not found")
    return db_contact_info

#Contact Info API Summary

#POST /contact_info/: Create new contact information.
#GET /contact_info/{contact_info_id}: Retrieve specific contact information by ID.
#GET /contact_info/: List all contact information entries with optional pagination.
#PUT /contact_info/{contact_info_id}: Update specific contact information by ID.
#DELETE /contact_info/{contact_info_id}: Delete specific contact information by ID