"""
Recommendation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Product, RecommendationLog, Category
from app.schemas import RecommendationRequest, RecommendationResponse, RecommendationLogCreate
from app.services import HybridRecommender
from app.services.cache import recommendation_cache
from app.services.content_based import ContentBasedService
from app.models.user_states import PurchaseHistory
from sqlalchemy import func, desc

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/top-pick", response_model=RecommendationResponse)
async def get_top_pick(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a single top recommendation for homepage display"""
    try:
        # Get user context if available
        user_id = None
        if hasattr(request.state, 'user_id') and request.state.user_id:
            try:
                user_id = UUID(request.state.user_id)
            except (ValueError, TypeError):
                user_id = None
        
        # Check cache first
        alpha = 0.5
        k = 1
        cached_result = recommendation_cache.get(user_id, None, alpha, k)
        if cached_result:
            return cached_result
        
        # Try to get a recommendation using the hybrid recommender
        try:
            recommender = HybridRecommender()
            # Get top recommendation with user context if available
            results = recommender.hybrid_recommend(
                user_id=user_id,
                query=None,
                alpha=alpha,  # Balanced approach
                k=k  # Just one top pick
            )
            
            if results:
                product_id, score, reason_features = results[0]
                
                # Get product details
                product = db.query(Product).filter(Product.product_id == product_id).first()
                if product:
                    # Get primary image
                    primary_image = None
                    for img in product.images:
                        if img.is_primary:
                            primary_image = img.cdn_url
                            break
                    
                    recommendation = RecommendationResponse(
                        product_id=product.product_id,
                        name=product.name,
                        price=product.price,
                        image_url=primary_image,
                        hybrid_score=score,
                        reason_features=reason_features
                    )
                    
                    # Cache the recommendation
                    recommendation_cache.set(user_id, None, alpha, k, recommendation)
                    
                    return recommendation
        except Exception as rec_error:
            print(f"Hybrid recommender failed: {str(rec_error)}")
        
        # Fallback: Get a random popular product
        import random
        products = db.query(Product).filter(Product.available == True).all()
        if not products:
            raise HTTPException(status_code=404, detail="No products available")
        
        product = random.choice(products)
        
        # Get primary image
        primary_image = None
        for img in product.images:
            if img.is_primary:
                primary_image = img.cdn_url
                break
        
        recommendation = RecommendationResponse(
            product_id=product.product_id,
            name=product.name,
            price=product.price,
            image_url=primary_image,
            hybrid_score=0.8,  # Default score
            reason_features={
                "matched_tags": product.tags or [],
                "cf_score": 0.8,
                "content_score": 0.8,
                "source": "fallback"
            }
        )
        
        # Cache the fallback recommendation
        recommendation_cache.set(user_id, None, alpha, k, recommendation)
        
        return recommendation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Top pick recommendation failed: {str(e)}")


@router.get("/hybrid", response_model=List[RecommendationResponse])
async def get_hybrid_recommendations(
    user_id: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    alpha: float = Query(0.6, ge=0.0, le=1.0),
    k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get hybrid recommendations combining content-based and collaborative filtering"""
    try:
        print(f"\n🎯 HYBRID RECOMMENDATION REQUEST")
        print(f"📥 Input Parameters:")
        print(f"   - user_id: {user_id}")
        print(f"   - query: {query}")
        print(f"   - alpha: {alpha}")
        print(f"   - k: {k}")
        
        # Validate and convert user_id to UUID if provided
        validated_user_id = None
        if user_id:
            try:
                validated_user_id = UUID(user_id)
                print(f"✅ Validated user_id: {validated_user_id}")
            except ValueError:
                print(f"⚠️ Invalid UUID format: {user_id}, proceeding without user_id")
                validated_user_id = None
        
        recommender = HybridRecommender()
        results = recommender.hybrid_recommend(
            user_id=validated_user_id,
            query=query,
            alpha=alpha,
            k=k,
            db=db
        )
        
        print(f"\n🔍 HYBRID RECOMMENDER RESULTS:")
        print(f"   - Total results: {len(results)}")
        for i, (product_id, score, reason_features) in enumerate(results, 1):
            print(f"   {i}. Product ID: {product_id}")
            print(f"      Hybrid Score: {score:.4f}")
            print(f"      Reason Features: {reason_features}")
        
        # Get product details
        product_ids = [result[0] for result in results]  # result[0] is already a UUID object
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        print(f"\n📦 PRODUCT DETAILS FETCHED:")
        print(f"   - Found {len(products)} products in database")
        
        # Create mapping and build response
        product_map = {p.product_id: p for p in products}
        recommendations = []
        
        print(f"\n🎁 FINAL RECOMMENDATIONS:")
        for i, (product_id, score, reason_features) in enumerate(results, 1):
            if product_id in product_map:
                product = product_map[product_id]
                
                # Get primary image
                primary_image = None
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.cdn_url
                        break
                
                recommendation = RecommendationResponse(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    discount_percent=product.discount_percent,
                    image_url=primary_image,
                    hybrid_score=score,
                    reason_features=reason_features
                )
                recommendations.append(recommendation)
                
                print(f"   {i}. {product.name}")
                print(f"      ID: {product.product_id}")
                print(f"      Price: ₹{product.price}")
                print(f"      Hybrid Score: {score:.4f}")
                print(f"      Content Score: {reason_features.get('content_score', 0):.4f}")
                print(f"      CF Score: {reason_features.get('cf_score', 0):.4f}")
                print(f"      Source: {reason_features.get('source', 'unknown')}")
                print(f"      Image: {primary_image}")
                print()
        
        # Log recommendation request (only if we have a valid user_id)
        if validated_user_id:
            try:
                log_entry = RecommendationLog(
                    user_id=validated_user_id,
                    request_context={
                        "query": query,
                        "alpha": alpha,
                        "k": k,
                        "type": "hybrid"
                    },
                    candidate_products=product_ids
                )
                db.add(log_entry)
                db.commit()
            except Exception:
                # Don't fail the whole request if logging fails
                db.rollback()
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.get("/content", response_model=List[RecommendationResponse])
async def get_content_recommendations(
    product_id: UUID = Query(...),
    k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get content-based recommendations for a product"""
    try:
        recommender = HybridRecommender()
        results = recommender.get_recommendation_for_product(
            product_id=product_id,
            k=k
        )
        
        # Get product details
        product_ids = [result[0] for result in results]
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        # Create mapping and build response
        product_map = {p.product_id: p for p in products}
        recommendations = []
        
        for pid, score, reason_features in results:
            if pid in product_map:
                product = product_map[pid]
                
                # Get primary image
                primary_image = None
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.cdn_url
                        break
                
                recommendation = RecommendationResponse(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    discount_percent=product.discount_percent,
                    image_url=primary_image,
                    hybrid_score=score,
                    reason_features=reason_features
                )
                recommendations.append(recommendation)
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content recommendation failed: {str(e)}")


@router.get("/collaborative", response_model=List[RecommendationResponse])
async def get_collaborative_recommendations(
    user_id: UUID = Query(...),
    k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get collaborative filtering recommendations"""
    try:
        # Get user's purchased product IDs to exclude
        purchased_product_ids = db.query(PurchaseHistory.product_id).filter(
            PurchaseHistory.user_id == user_id,
            PurchaseHistory.payment_status == 'completed'
        ).distinct().all()
        purchased_ids_set = {pid[0] for pid in purchased_product_ids}
        print(f"📦 Excluding {len(purchased_ids_set)} purchased products from collaborative recommendations")
        
        from app.services import CollaborativeService
        cf_service = CollaborativeService()
        
        # Get more results to account for filtering out purchased items
        results = cf_service.get_user_recommendations(user_id, k=k * 2)
        
        # Filter out purchased items
        filtered_results = [(pid, score) for pid, score in results if pid not in purchased_ids_set]
        filtered_results = filtered_results[:k]  # Take top k after filtering
        
        # Get product details
        product_ids = [result[0] for result in filtered_results]
        if not product_ids:
            return []
        
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        # Create mapping and build response
        product_map = {p.product_id: p for p in products}
        recommendations = []
        
        # Results already contain normalized scores (normalized across all items)
        # Scale: 0.5-1.0 range (since these are top items)
        if filtered_results:
            for product_id, normalized_score in filtered_results:
                if product_id in product_map:
                    product = product_map[product_id]
                    
                    # Get primary image
                    primary_image = None
                    for img in product.images:
                        if img.is_primary:
                            primary_image = img.cdn_url
                            break
                    
                    recommendation = RecommendationResponse(
                        product_id=product.product_id,
                        name=product.name,
                        price=product.price,
                        discount_percent=product.discount_percent,
                        image_url=primary_image,
                        hybrid_score=normalized_score,
                        reason_features={
                            "cf_score": normalized_score,
                            "source": "collaborative"
                        }
                    )
                    recommendations.append(recommendation)
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collaborative recommendation failed: {str(e)}")


@router.get("/personalized", response_model=List[RecommendationResponse])
async def get_personalized_recommendations(
    user_id: UUID = Query(...),
    k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for logged-in user"""
    try:
        recommender = HybridRecommender()
        results = recommender.hybrid_recommend(
            user_id=user_id,
            alpha=0.7,  # Higher weight for collaborative filtering for personalized
            k=k
        )
        
        # Get product details
        product_ids = [result[0] for result in results]
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        # Create mapping and build response
        product_map = {p.product_id: p for p in products}
        recommendations = []
        
        for product_id, score, reason_features in results:
            if product_id in product_map:
                product = product_map[product_id]
                
                # Get primary image
                primary_image = None
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.cdn_url
                        break
                
                recommendation = RecommendationResponse(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    discount_percent=product.discount_percent,
                    image_url=primary_image,
                    hybrid_score=score,
                    reason_features=reason_features
                )
                recommendations.append(recommendation)
        
        # Log recommendation request
        log_entry = RecommendationLog(
            user_id=user_id,
            request_context={
                "type": "personalized",
                "k": k
            },
            candidate_products=product_ids
        )
        db.add(log_entry)
        db.commit()
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Personalized recommendation failed: {str(e)}")


@router.get("/top-sellers", response_model=List[RecommendationResponse])
async def get_top_sellers(
    k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get top sellers - most purchased products in the database"""
    try:
        # Query products by purchase count from purchase_history table
        top_sellers_query = db.query(
            PurchaseHistory.product_id,
            func.count(PurchaseHistory.id).label('purchase_count')
        ).filter(
            PurchaseHistory.payment_status == 'completed'
        ).group_by(
            PurchaseHistory.product_id
        ).order_by(
            desc('purchase_count')
        ).limit(k).all()
        
        if not top_sellers_query:
            # Fallback to random popular products if no purchase history
            products = db.query(Product).filter(Product.available == True).limit(k).all()
            recommendations = []
            for product in products:
                primary_image = None
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.cdn_url
                        break
                
                recommendations.append(RecommendationResponse(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    discount_percent=product.discount_percent,
                    image_url=primary_image,
                    hybrid_score=0.8,
                    reason_features={
                        "source": "top_sellers_fallback",
                        "purchase_count": 0
                    }
                ))
            return recommendations
        
        # Get product IDs and purchase counts
        product_ids = [result.product_id for result in top_sellers_query]
        purchase_counts = {result.product_id: result.purchase_count for result in top_sellers_query}
        
        # Get product details
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        # Create mapping and build response (maintain order by purchase count)
        product_map = {p.product_id: p for p in products}
        recommendations = []
        
        for product_id in product_ids:
            if product_id in product_map:
                product = product_map[product_id]
                
                # Get primary image
                primary_image = None
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.cdn_url
                        break
                
                # Normalize purchase count to score (0.8-1.0 range)
                max_count = max(purchase_counts.values())
                purchase_count = purchase_counts.get(product_id, 0)
                score = 0.8 + (0.2 * (purchase_count / max_count)) if max_count > 0 else 0.8
                
                recommendation = RecommendationResponse(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    discount_percent=product.discount_percent,
                    image_url=primary_image,
                    hybrid_score=score,
                    reason_features={
                        "source": "top_sellers",
                        "purchase_count": purchase_count
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Top sellers recommendation failed: {str(e)}")


@router.get("/content-based", response_model=List[RecommendationResponse])
async def get_content_based_recommendations(
    user_id: UUID = Query(...),
    k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get content-based recommendations for logged-in user by aggregating purchase history, wishlist, and cart"""
    try:
        # Get user's purchased product IDs to exclude
        purchased_product_ids = db.query(PurchaseHistory.product_id).filter(
            PurchaseHistory.user_id == user_id,
            PurchaseHistory.payment_status == 'completed'
        ).distinct().all()
        purchased_ids_set = {pid[0] for pid in purchased_product_ids}
        print(f"📦 Excluding {len(purchased_ids_set)} purchased products from recommendations")
        
        content_service = ContentBasedService()
        results = content_service.get_user_content_recommendations_from_all_sources(
            user_id=user_id,
            db=db,
            k=k * 2  # Get more results to account for filtering
        )
        
        # Filter out purchased items
        filtered_results = [(pid, score) for pid, score in results if pid not in purchased_ids_set]
        filtered_results = filtered_results[:k]  # Take top k after filtering
        
        # Get product details
        product_ids = [result[0] for result in filtered_results]
        if not product_ids:
            return []
        
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        # Create mapping and build response
        product_map = {p.product_id: p for p in products}
        recommendations = []
        
        for product_id, score in filtered_results:
            if product_id in product_map:
                product = product_map[product_id]
                
                # Get primary image
                primary_image = None
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.cdn_url
                        break
                
                recommendation = RecommendationResponse(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    discount_percent=product.discount_percent,
                    image_url=primary_image,
                    hybrid_score=score,
                    reason_features={
                        "content_score": score,
                        "source": "content_based_all_sources"
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content-based recommendation failed: {str(e)}")


@router.get("/product-you-may-also-like", response_model=List[RecommendationResponse])
async def get_product_you_may_also_like(
    product_id: UUID = Query(...),
    user_id: Optional[UUID] = Query(None),
    k: int = Query(8, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get hybrid recommendations for a product page:
    - Content-based: Similar to current product
    - Collaborative: User preferences within parent category (alpha=0.4, content=40%, collab=60%)
    """
    try:
        # Get current product
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get parent category
        parent_category_id = None
        if product.category_id:
            category = db.query(Category).filter(Category.category_id == product.category_id).first()
            if category:
                # If category has a parent, use parent. Otherwise, use current category (it's already a parent)
                parent_category_id = category.parent_id if category.parent_id else category.category_id
                print(f"📂 Product category: {category.name} (ID: {category.category_id})")
                print(f"📂 Parent category ID: {parent_category_id}")
        
        # Get all products in parent category (excluding subcategories)
        category_product_ids = []
        if parent_category_id:
            category_products = db.query(Product.product_id).filter(
                Product.category_id == parent_category_id,
                Product.available == True,
                Product.product_id != product_id  # Exclude current product
            ).all()
            category_product_ids = [p[0] for p in category_products]
            print(f"📦 Found {len(category_product_ids)} products in parent category")
        else:
            print(f"⚠️ No category found for product")
        
        # Get user's purchased product IDs to exclude
        purchased_ids_set = set()
        if user_id:
            purchased_product_ids = db.query(PurchaseHistory.product_id).filter(
                PurchaseHistory.user_id == user_id,
                PurchaseHistory.payment_status == 'completed'
            ).distinct().all()
            purchased_ids_set = {pid[0] for pid in purchased_product_ids}
            print(f"📦 Excluding {len(purchased_ids_set)} purchased products")
        
        # Content-based: Find similar products to current product
        from app.services import ContentBasedService, CollaborativeService
        content_service = ContentBasedService()
        content_results = content_service.find_similar_products(product_id, k=k * 2)
        
        # Filter out current product and purchased items
        content_results = [
            (pid, score) for pid, score in content_results 
            if pid != product_id and pid not in purchased_ids_set
        ][:k]
        
        print(f"📝 Content-based results: {len(content_results)} products")
        
        # Collaborative: Get user recommendations filtered to parent category products
        cf_results = []
        if user_id and category_product_ids:
            cf_service = CollaborativeService()
            cf_results = cf_service.get_user_recommendations_filtered_by_category(
                user_id=user_id,
                category_product_ids=category_product_ids,
                k=k * 2
            )
            # Filter out purchased items
            cf_results = [
                (pid, score) for pid, score in cf_results 
                if pid not in purchased_ids_set and pid != product_id
            ][:k]
            print(f"🤝 Collaborative results (category-filtered): {len(cf_results)} products")
        
        # Normalize scores
        from app.services.recommender import HybridRecommender
        recommender = HybridRecommender()
        content_scores = recommender._normalize_scores(content_results)
        cf_scores = recommender._normalize_scores(cf_results)
        
        # Combine with alpha=0.4 (content=40%, collab=60%)
        alpha = 0.4  # Collaborative weight
        hybrid_scores = {}
        
        # Add content scores (weight = 0.6)
        for pid, score in content_scores.items():
            hybrid_scores[pid] = {
                "content_score": score,
                "cf_score": 0.0,
                "hybrid_score": (1 - alpha) * score,  # 0.6 * score
                "source": "hybrid_content"
            }
        
        # Add collaborative scores (weight = 0.4)
        for pid, score in cf_scores.items():
            if pid in hybrid_scores:
                hybrid_scores[pid]["cf_score"] = score
                hybrid_scores[pid]["hybrid_score"] += alpha * score  # 0.4 * score
                hybrid_scores[pid]["source"] = "hybrid"
            else:
                hybrid_scores[pid] = {
                    "content_score": 0.0,
                    "cf_score": score,
                    "hybrid_score": alpha * score,  # 0.4 * score
                    "source": "hybrid_collaborative"
                }
        
        # Sort by hybrid score and get top-k
        sorted_results = sorted(
            hybrid_scores.items(),
            key=lambda x: x[1]["hybrid_score"],
            reverse=True
        )[:k]
        
        # Get product details
        product_ids = [result[0] for result in sorted_results]
        if not product_ids:
            return []
        
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        product_map = {p.product_id: p for p in products}
        recommendations = []
        
        # Build response in the order of hybrid scores
        for product_id, scores in sorted_results:
            if product_id in product_map:
                product = product_map[product_id]
                
                # Get primary image
                primary_image = None
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.cdn_url
                        break
                
                recommendation = RecommendationResponse(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    discount_percent=product.discount_percent,
                    image_url=primary_image,
                    hybrid_score=scores["hybrid_score"],
                    reason_features={
                        "content_score": scores["content_score"],
                        "cf_score": scores["cf_score"],
                        "source": scores["source"],
                        "hybrid": True
                    }
                )
                recommendations.append(recommendation)
        
        print(f"✅ Returning {len(recommendations)} hybrid recommendations (alpha={alpha})")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting product recommendations: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/user-item-similarity")
async def get_user_item_similarity(
    user_id: UUID = Query(...),
    product_id: UUID = Query(...),
    db: Session = Depends(get_db)
):
    """Get user-item similarity score for collaborative filtering"""
    try:
        from app.services import CollaborativeService
        cf_service = CollaborativeService()
        
        # Get score with proper normalization relative to all items for this user
        raw_score, normalized_score = cf_service.get_collaborative_score_with_normalization(user_id, product_id)
        
        print(f"📊 User-Item Similarity:")
        print(f"   - User ID: {user_id}")
        print(f"   - Product ID: {product_id}")
        print(f"   - Raw Score: {raw_score:.4f}")
        print(f"   - Normalized Score: {normalized_score:.4f} (relative to all items)")
        
        return {
            "user_id": str(user_id),
            "product_id": str(product_id),
            "similarity_score": raw_score,
            "normalized_score": normalized_score
        }
        
    except Exception as e:
        print(f"Error getting user-item similarity: {e}")
        import traceback
        traceback.print_exc()
        # Return default score if error
        return {
            "user_id": str(user_id),
            "product_id": str(product_id),
            "similarity_score": 0.0,
            "normalized_score": 0.0
        }

