import { useState, useEffect } from 'react';
import { reviewService, ReviewWithUser, RatingSummary } from '../services/reviewService';
import { useAuth } from '@/contexts/AuthContext';
import { interactionService } from '@/services/interactionService';
import { Star, MessageSquare, Plus, Check, ThumbsUp, Edit, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';

interface ReviewSectionProps {
  productId: string;
}

export const ReviewSection = ({ productId }: ReviewSectionProps) => {
  const { user, isAuthenticated } = useAuth();
  const [reviews, setReviews] = useState<ReviewWithUser[]>([]);
  const [ratingSummary, setRatingSummary] = useState<RatingSummary | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editingReviewId, setEditingReviewId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sortBy, setSortBy] = useState('newest');
  
  // Form state
  const [rating, setRating] = useState(5);
  const [title, setTitle] = useState('');
  const [comment, setComment] = useState('');

  useEffect(() => {
    loadReviews();
    loadRatingSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [productId, sortBy]);

  const loadReviews = async () => {
    try {
      setIsLoading(true);
      const data = await reviewService.getProductReviews(productId, 1, 50, sortBy);
      setReviews(data || []);
    } catch (error) {
      console.error('Failed to load reviews:', error);
      setReviews([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadRatingSummary = async () => {
    try {
      const summary = await reviewService.getProductRatingSummary(productId);
      setRatingSummary(summary);
    } catch (error) {
      console.error('Failed to load rating summary:', error);
    }
  };

  const handleSubmitReview = async () => {
    if (!isAuthenticated) {
      alert('Please log in to submit a review');
      return;
    }

    try {
      if (isEditing && editingReviewId) {
        // Update existing review
        await reviewService.updateReview(editingReviewId, {
          rating,
          title: title || undefined,
          comment: comment || undefined,
        });
      } else {
        // Create new review
        await reviewService.createReview({
          product_id: productId,
          rating,
          title: title || undefined,
          comment: comment || undefined,
        });
        
        // Track review interaction
        interactionService.trackReview(productId, rating, comment, {
          page: 'product_detail',
          product_id: productId,
          rating: rating,
          has_comment: !!comment,
          comment_length: comment?.length || 0,
          has_title: !!title,
          timestamp: new Date().toISOString()
        });

        // Dispatch custom event for console logging
        window.dispatchEvent(new CustomEvent('reviewSubmitted', {
          detail: {
            productId,
            rating,
            comment,
            title,
            timestamp: new Date().toISOString()
          }
        }));
      }
      
      // Reset form
      setRating(5);
      setTitle('');
      setComment('');
      setIsDialogOpen(false);
      setIsEditing(false);
      setEditingReviewId(null);
      
      // Reload reviews
      loadReviews();
      loadRatingSummary();
    } catch (error: any) {
      console.error('Failed to submit review:', error);
      
      // Show specific error message
      if (error.message && error.message.includes('already reviewed')) {
        alert('You have already reviewed this product. You can only submit one review per product.');
      } else {
        alert('Failed to submit review. Please try again.');
      }
    }
  };

  const handleEditReview = (review: ReviewWithUser) => {
    setRating(review.rating);
    setTitle(review.title || '');
    setComment(review.comment || '');
    setIsEditing(true);
    setEditingReviewId(review.review_id);
    setIsDialogOpen(true);
  };

  const handleDeleteReview = async (reviewId: string) => {
    if (!confirm('Are you sure you want to delete this review?')) {
      return;
    }

    try {
      await reviewService.deleteReview(reviewId);
      loadReviews();
      loadRatingSummary();
    } catch (error) {
      console.error('Failed to delete review:', error);
      alert('Failed to delete review. Please try again.');
    }
  };

  const handleOpenDialog = () => {
    // Reset form when opening fresh dialog
    if (!isEditing) {
      setRating(5);
      setTitle('');
      setComment('');
      setEditingReviewId(null);
    }
    setIsDialogOpen(true);
  };

  const handleHelpful = async (reviewId: string) => {
    if (!user) {
      alert('Please login to mark reviews as helpful');
      return;
    }

    try {
      await reviewService.markHelpful(reviewId);
      loadReviews();
    } catch (error) {
      console.error('Failed to mark helpful:', error);
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
        }`}
      />
    ));
  };

  const renderRatingBar = (stars: number, count: number, total: number) => {
    const percentage = total > 0 ? (count / total) * 100 : 0;
    
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm w-8">{stars} ★</span>
        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className="text-sm text-muted-foreground w-12 text-right">
          {count}
        </span>
      </div>
    );
  };

  return (
    <section className="mt-16 border-t pt-8">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h2 className="text-2xl font-bold text-foreground mb-2">Customer Reviews</h2>
          {ratingSummary && (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-3xl font-bold">{ratingSummary.average_rating.toFixed(1)}</span>
                <div className="flex gap-1">
                  {renderStars(Math.round(ratingSummary.average_rating))}
                </div>
              </div>
              <span className="text-muted-foreground">
                Based on {ratingSummary.total_reviews} {ratingSummary.total_reviews === 1 ? 'review' : 'reviews'}
              </span>
            </div>
          )}
        </div>
        
        {isAuthenticated && (
          <Button onClick={handleOpenDialog}>
            <Plus className="w-4 h-4 mr-2" />
            Write a Review
          </Button>
        )}
      </div>

      {/* Rating Distribution */}
      {ratingSummary && ratingSummary.total_reviews > 0 && (
        <div className="bg-muted/30 rounded-lg p-6 mb-8">
          <h3 className="font-semibold mb-4">Rating Breakdown</h3>
          <div className="space-y-2">
            {[5, 4, 3, 2, 1].map((stars) => (
              <div key={stars}>
                {renderRatingBar(
                  stars,
                  ratingSummary.rating_distribution[stars] || 0,
                  ratingSummary.total_reviews
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sort Options */}
      {reviews.length > 0 && (
        <div className="flex gap-2 mb-6">
          <Button
            variant={sortBy === 'newest' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSortBy('newest')}
          >
            Newest
          </Button>
          <Button
            variant={sortBy === 'oldest' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSortBy('oldest')}
          >
            Oldest
          </Button>
          <Button
            variant={sortBy === 'rating_high' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSortBy('rating_high')}
          >
            Highest Rated
          </Button>
          <Button
            variant={sortBy === 'rating_low' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSortBy('rating_low')}
          >
            Lowest Rated
          </Button>
        </div>
      )}

      {/* Reviews List */}
      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading reviews...</p>
        </div>
      ) : reviews.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No reviews yet. Be the first to review this product!</p>
        </div>
      ) : (
        <div className="space-y-6">
          {reviews.map((review) => (
            <div key={review.review_id} className="border-b pb-6 last:border-0 last:pb-0">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold">
                      {review.user?.username || 'Anonymous'}
                    </span>
                    {review.verified_purchase && (
                      <Badge variant="secondary" className="text-xs">
                        <Check className="w-3 h-3 mr-1" />
                        Verified Purchase
                      </Badge>
                    )}
                  </div>
                  <div className="flex gap-2 items-center">
                    <div className="flex gap-1">
                      {renderStars(review.rating)}
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {new Date(review.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                {/* Edit/Delete buttons for user's own reviews */}
                {isAuthenticated && user && review.user_id === user.user_id && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEditReview(review)}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteReview(review.review_id)}
                      className="text-sm text-muted-foreground hover:text-destructive transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
              
              {review.title && (
                <h4 className="font-semibold mb-2">{review.title}</h4>
              )}
              
              {review.comment && (
                <p className="text-muted-foreground whitespace-pre-wrap mb-3">{review.comment}</p>
              )}

              {/* Helpful Button - Hidden for now */}
              {/* <button 
                onClick={() => handleHelpful(review.review_id)}
                className="flex items-center gap-1 hover:text-primary transition-colors text-sm text-muted-foreground"
                disabled={!user}
              >
                <ThumbsUp className="w-4 h-4" />
                Helpful ({review.helpful_count})
              </button> */}
            </div>
          ))}
        </div>
      )}

      {/* Write Review Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{isEditing ? 'Edit Review' : 'Write a Review'}</DialogTitle>
            <DialogDescription>
              {isEditing ? 'Update your review' : 'Share your experience with this product'}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Rating</label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className="focus:outline-none"
                  >
                    <Star
                      className={`w-8 h-8 ${
                        star <= rating
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Title (optional)</label>
              <Input
                placeholder="Summarize your review"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={100}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Review</label>
              <Textarea
                placeholder="Share your thoughts about this product..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={4}
                maxLength={1000}
              />
              <p className="text-xs text-muted-foreground mt-1">
                {comment.length}/1000 characters
              </p>
            </div>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmitReview} disabled={!rating}>
              {isEditing ? 'Update Review' : 'Submit Review'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </section>
  );
};
