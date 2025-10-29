from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Review, User, Product, ReviewHelpfulVote
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewWithUser, ReviewUpdate, ProductRatingSummary

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


# Dependency to get current user (optional for public endpoints)
def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current user from request state and database - optional, won't fail if not authenticated"""
    user_id = getattr(request.state, 'user_id', None)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = db.query(User).filter(User.user_id == UUID(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Create a new review"""
    # Check if user already reviewed this product
    existing_review = db.query(Review).filter(
        Review.user_id == current_user.user_id,
        Review.product_id == review_data.product_id
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    # Check if product exists
    product = db.query(Product).filter(Product.product_id == review_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user has purchased the product (optional verification)
    verified_purchase = False  # Implement purchase verification logic
    
    review = Review(
        user_id=current_user.user_id,
        product_id=review_data.product_id,
        rating=review_data.rating,
        title=review_data.title,
        comment=review_data.comment,
        verified_purchase=verified_purchase
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # Update product rating
    review.update_product_rating(db)
    
    return review


@router.get("/product/{product_id}", response_model=List[ReviewWithUser])
async def get_product_reviews(
    product_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    sort: str = Query("newest", regex="^(newest|oldest|rating_high|rating_low)$"),
    db: Session = Depends(get_db)
):
    """Get reviews for a product"""
    query = db.query(Review, User).join(User).filter(
        Review.product_id == product_id,
        Review.is_approved == True
    )
    
    # Sorting
    if sort == "newest":
        query = query.order_by(Review.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(Review.created_at.asc())
    elif sort == "rating_high":
        query = query.order_by(Review.rating.desc())
    elif sort == "rating_low":
        query = query.order_by(Review.rating.asc())
    
    # Pagination
    reviews = query.offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for review, user in reviews:
        review_dict = ReviewResponse.model_validate(review).model_dump()
        review_dict['user'] = {
            'username': user.username or 'Anonymous',
            'is_anonymous': user.is_anonymous
        }
        result.append(ReviewWithUser(**review_dict))
    
    return result


@router.get("/product/{product_id}/summary", response_model=ProductRatingSummary)
async def get_product_rating_summary(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """Get rating summary for a product"""
    # Get average rating and total count
    stats = db.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.review_id).label('total_reviews')
    ).filter(
        Review.product_id == product_id,
        Review.is_approved == True
    ).first()
    
    # Get rating distribution
    distribution = db.query(
        Review.rating,
        func.count(Review.review_id).label('count')
    ).filter(
        Review.product_id == product_id,
        Review.is_approved == True
    ).group_by(Review.rating).all()
    
    rating_dist = {i: 0 for i in range(1, 6)}
    for rating, count in distribution:
        rating_dist[rating] = count
    
    return ProductRatingSummary(
        average_rating=round(stats.avg_rating or 0.0, 1),
        total_reviews=stats.total_reviews or 0,
        rating_distribution=rating_dist
    )


@router.get("/user/{user_id}", response_model=List[ReviewWithUser])
async def get_user_reviews(
    user_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get reviews by a specific user"""
    query = db.query(Review, User, Product).join(
        User, Review.user_id == User.user_id
    ).join(
        Product, Review.product_id == Product.product_id
    ).filter(
        Review.user_id == user_id
    ).order_by(Review.created_at.desc())
    
    # Pagination
    reviews = query.offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for review, user, product in reviews:
        review_dict = ReviewResponse.model_validate(review).model_dump()
        review_dict['user'] = {
            'username': user.username or 'Anonymous',
            'is_anonymous': user.is_anonymous
        }
        review_dict['product_name'] = product.name
        result.append(ReviewWithUser(**review_dict))
    
    return result


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Update own review"""
    review = db.query(Review).filter(Review.review_id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own reviews")
    
    if review_data.rating is not None:
        review.rating = review_data.rating
    if review_data.title is not None:
        review.title = review_data.title
    if review_data.comment is not None:
        review.comment = review_data.comment
    
    db.commit()
    db.refresh(review)
    
    # Update product rating
    review.update_product_rating(db)
    
    return review


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Delete own review"""
    review = db.query(Review).filter(Review.review_id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")
    
    product_id = review.product_id
    db.delete(review)
    db.commit()
    
    # Update product rating using a new review instance to call the method
    temp_review = Review()
    temp_review.product_id = product_id
    temp_review.update_product_rating(db)


@router.post("/{review_id}/helpful", status_code=200)
async def mark_review_helpful(
    review_id: UUID,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Toggle helpful vote on a review"""
    review = db.query(Review).filter(Review.review_id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if user has already voted
    existing_vote = db.query(ReviewHelpfulVote).filter(
        ReviewHelpfulVote.review_id == review_id,
        ReviewHelpfulVote.user_id == current_user.user_id
    ).first()
    
    if existing_vote:
        # Remove vote (decrement)
        db.delete(existing_vote)
        review.helpful_count -= 1
    else:
        # Add vote (increment)
        vote = ReviewHelpfulVote(
            review_id=review_id,
            user_id=current_user.user_id
        )
        db.add(vote)
        review.helpful_count += 1
    
    db.commit()
    db.refresh(review)
    
    return {"helpful_count": review.helpful_count}
