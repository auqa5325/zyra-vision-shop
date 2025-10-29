import { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { RefreshCw, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import apiClient from "@/services/api";

interface ModelStatus {
  faiss_loaded: boolean;
  sentence_transformer_loaded: boolean;
  als_loaded: boolean;
  als_users_count: number;
  als_items_count: number;
}

const AdminPage = () => {
  const { toast } = useToast();
  const [isRetraining, setIsRetraining] = useState(false);
  const [isReloading, setIsReloading] = useState(false);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);

  const fetchModelStatus = async () => {
    console.log("🔍 Fetching model status...");
    setIsLoadingStatus(true);
    
    try {
      const status = await apiClient.get<ModelStatus>("/api/admin/model-status");
      console.log("📊 Model status received:", status);
      setModelStatus(status);
      
      // Log detailed status
      console.log("📋 Model Status Details:", {
        "FAISS Index": status.faiss_loaded ? "✅ Loaded" : "❌ Not loaded",
        "Sentence Transformer": status.sentence_transformer_loaded ? "✅ Loaded" : "❌ Not loaded",
        "ALS Model": status.als_loaded ? "✅ Loaded" : "❌ Not loaded",
        "ALS Users": status.als_users_count,
        "ALS Items": status.als_items_count
      });
      
    } catch (error) {
      console.error("❌ Failed to fetch model status:", error);
      console.error("Error details:", {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      toast({
        title: "Error",
        description: "Failed to fetch model status",
        variant: "destructive",
      });
    } finally {
      console.log("🏁 Model status fetch completed");
      setIsLoadingStatus(false);
    }
  };

  const handleRetrainAndReload = async () => {
    console.log("🔄 Starting ALS model retraining...");
    setIsRetraining(true);
    
    try {
      console.log("📡 Sending retrain request to backend...");
      const response = await apiClient.post<{
        success: boolean;
        message: string;
        interaction_count: number;
      }>("/api/admin/retrain-and-reload-als");

      console.log("📥 Retrain response received:", response);

      if (response.success) {
        console.log("✅ Retraining started successfully");
        console.log(`📊 Interaction count: ${response.interaction_count}`);
        
        toast({
          title: "Success",
          description: "ALS model retraining started in background. The model will reload automatically when complete.",
        });

        // Poll for completion with more frequent checks
        console.log("⏰ Starting status polling...");
        let pollCount = 0;
        const maxPolls = 12; // Poll for up to 2 minutes (10s intervals)
        
        const pollInterval = setInterval(async () => {
          pollCount++;
          console.log(`🔍 Polling status (${pollCount}/${maxPolls})...`);
          
          try {
            await fetchModelStatus();
            console.log("📊 Status updated");
            
            if (pollCount >= maxPolls) {
              clearInterval(pollInterval);
              console.log("⏰ Polling completed - check status manually");
              toast({
                title: "Model Training",
                description: "Training may take a few minutes. Check status periodically.",
              });
            }
          } catch (error) {
            console.error("❌ Error during status polling:", error);
            clearInterval(pollInterval);
          }
        }, 10000); // Poll every 10 seconds

        // Also check status after 5 seconds
        setTimeout(async () => {
          console.log("🔍 Initial status check after 5 seconds...");
          await fetchModelStatus();
        }, 5000);
        
      } else {
        console.error("❌ Retraining failed:", response.message);
        toast({
          title: "Error",
          description: response.message || "Failed to start retraining",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      console.error("❌ Failed to retrain model:", error);
      console.error("Error details:", {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      toast({
        title: "Error",
        description: error.message || "Failed to start model retraining",
        variant: "destructive",
      });
    } finally {
      console.log("🏁 Retraining request completed");
      setIsRetraining(false);
    }
  };

  const handleReloadModel = async () => {
    console.log("🔄 Starting model reload...");
    setIsReloading(true);
    
    try {
      console.log("📡 Sending reload request to backend...");
      const response = await apiClient.post<{
        success: boolean;
        message: string;
        users_count: number;
        items_count: number;
      }>("/api/admin/reload-als-model");

      console.log("📥 Reload response received:", response);

      if (response.success) {
        console.log("✅ Model reloaded successfully");
        console.log(`👥 Users: ${response.users_count}, Items: ${response.items_count}`);
        
        toast({
          title: "Success",
          description: `Model reloaded successfully. ${response.users_count} users, ${response.items_count} items.`,
        });
        
        console.log("🔍 Fetching updated model status...");
        await fetchModelStatus();
      } else {
        console.error("❌ Model reload failed:", response.message);
        toast({
          title: "Error",
          description: "Failed to reload model",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      console.error("❌ Failed to reload model:", error);
      console.error("Error details:", {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      toast({
        title: "Error",
        description: error.message || "Failed to reload model",
        variant: "destructive",
      });
    } finally {
      console.log("🏁 Model reload request completed");
      setIsReloading(false);
    }
  };

  // Fetch status on mount
  useEffect(() => {
    console.log("🚀 Admin page mounted, fetching initial model status...");
    fetchModelStatus();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <main className="flex-1 container px-4 py-12 max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Admin Panel</h1>
          <p className="text-muted-foreground">
            Manage and retrain the ALS recommendation model
          </p>
        </div>

        {/* Model Status Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Model Status</CardTitle>
                <CardDescription>Current state of loaded ML models</CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchModelStatus}
                disabled={isLoadingStatus}
              >
                {isLoadingStatus ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {modelStatus ? (
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  {modelStatus.faiss_loaded ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  <span className="text-sm">FAISS Index</span>
                </div>
                <div className="flex items-center gap-2">
                  {modelStatus.sentence_transformer_loaded ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  <span className="text-sm">Sentence Transformer</span>
                </div>
                <div className="flex items-center gap-2">
                  {modelStatus.als_loaded ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  <span className="text-sm">ALS Model</span>
                </div>
                {modelStatus.als_loaded && (
                  <>
                    <div className="text-sm">
                      <span className="text-muted-foreground">Users: </span>
                      <span className="font-semibold">{modelStatus.als_users_count}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-muted-foreground">Items: </span>
                      <span className="font-semibold">{modelStatus.als_items_count}</span>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">Loading status...</p>
            )}
          </CardContent>
        </Card>

        {/* Actions Card */}
        <Card>
          <CardHeader>
            <CardTitle>Model Training</CardTitle>
            <CardDescription>
              Retrain the ALS collaborative filtering model with updated interaction data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Retrain & Reload:</strong> Trains a new ALS model using all current interactions 
                and automatically reloads it into memory. This process runs in the background and may take 
                several minutes.
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>Reload Only:</strong> Reloads the existing trained model from disk without retraining.
              </p>
            </div>

            <div className="flex gap-4">
              <Button
                onClick={handleRetrainAndReload}
                disabled={isRetraining || isReloading}
                className="flex-1"
              >
                {isRetraining ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Retraining...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Retrain & Reload Model
                  </>
                )}
              </Button>

              <Button
                variant="outline"
                onClick={handleReloadModel}
                disabled={isRetraining || isReloading}
              >
                {isReloading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Reloading...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reload Model
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default AdminPage;

