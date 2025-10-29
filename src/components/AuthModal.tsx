import { Button } from "@/components/ui/button";
import { LogIn } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { useNavigate } from "react-router-dom";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  action?: string; // "cart", "wishlist", etc.
}

export const AuthModal = ({ isOpen, onClose, action = "continue" }: AuthModalProps) => {
  const navigate = useNavigate();

  const handleLogin = () => {
    onClose();
    navigate("/login");
  };

  const getActionText = () => {
    switch (action) {
      case "cart":
        return "add items to cart";
      case "wishlist":
        return "add items to wishlist";
      default:
        return "continue";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <LogIn className="w-5 h-5" />
            Sign In Required
          </DialogTitle>
          <DialogDescription>
            Please sign in to {getActionText()}.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            You need to be signed in to {getActionText()}. Click the button below to go to the login page.
          </p>

          <div className="flex flex-col gap-3">
            <Button onClick={handleLogin} className="w-full">
              <LogIn className="w-4 h-4 mr-2" />
              Go to Login Page
            </Button>

            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="w-full"
            >
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
