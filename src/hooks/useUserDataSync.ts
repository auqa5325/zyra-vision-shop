/**
 * Simple User Data Sync hook - Basic stats fetching only
 */
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { userDataService } from '@/services/userDataService';

export const useUserDataSync = () => {
  const { isAuthenticated, user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [userStats, setUserStats] = useState<any>(null);

  // Fetch user stats when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      // Add small delay to prevent race conditions
      const timeoutId = setTimeout(() => {
        fetchUserStats();
      }, 100);
      
      return () => clearTimeout(timeoutId);
    } else {
      setUserStats(null);
    }
  }, [isAuthenticated, user]);

  const fetchUserStats = async () => {
    if (!isAuthenticated || !user) {
      return;
    }

    setIsLoading(true);
    try {
      
      // Fetch both stats and purchase history in parallel
      const [stats, purchases] = await Promise.all([
        userDataService.getUserStats(),
        userDataService.getPurchaseHistoryFromDB()
      ]);
      
      // Combine stats with purchase history
      const combinedStats = {
        ...stats,
        purchases: purchases // Replace the number with the actual purchase array
      };
      
      setUserStats(combinedStats);
    } catch (error) {
      console.error('❌ [USER DATA SYNC] Failed to fetch stats:', error);
      // Set default stats on error
      setUserStats({
        total_interactions: 0,
        event_types: {},
        platforms: {},
        last_activity: null,
        totalSpent: 0,
        purchases: []
      });
    } finally {
      setIsLoading(false);
    }
  };

  const refreshData = () => {
    if (isAuthenticated && user) {
      fetchUserStats();
    } else {
    }
  };

  return {
    isLoading,
    userStats,
    refreshData
  };
};