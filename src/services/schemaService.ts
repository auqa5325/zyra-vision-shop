/**
 * Schema service for database and API information
 */

import apiClient from './api';

export interface TableColumn {
  name: string;
  type: string;
  nullable: boolean;
  default: string | null;
  primary_key: boolean;
  autoincrement: boolean;
  comment?: string;
}

export interface ForeignKey {
  constrained_columns: string[];
  referred_table: string;
  referred_columns: string[];
  name?: string;
}

export interface TableIndex {
  name: string;
  columns: string[];
  unique: boolean;
  type?: string;
}

export interface TableInfo {
  columns: TableColumn[];
  foreign_keys: ForeignKey[];
  indexes: TableIndex[];
}

export interface DatabaseSchema {
  tables: Record<string, TableInfo>;
  relationships: Array<{
    table: string;
    relationship: string;
    target_table: string;
    relationship_type: string;
  }>;
  indexes: Record<string, any>;
  constraints: Record<string, any>;
}

export interface TableDetails {
  table_name: string;
  columns: TableColumn[];
  foreign_keys: ForeignKey[];
  indexes: TableIndex[];
  row_count: number;
  sample_data: Record<string, any>[];
}

export interface DatabaseStats {
  tables: Record<string, {
    row_count: number;
    size: string;
    size_bytes: number;
  }>;
  total_tables: number;
  total_rows: number;
}

export interface APIEndpoint {
  path: string;
  method: string;
  description: string;
  requires_auth: boolean;
  request_schema?: string;
  response_schema?: string;
  query_params?: string[];
}

export interface APIGroup {
  base_path: string;
  endpoints: APIEndpoint[];
}

export interface APIInfo {
  [key: string]: APIGroup;
}

class SchemaService {
  /**
   * Get complete database schema
   */
  async getDatabaseSchema(): Promise<DatabaseSchema> {
    try {
      const response = await apiClient.get<DatabaseSchema>('/api/schema/tables');
      return response;
    } catch (error) {
      console.error('Failed to get database schema:', error);
      throw error;
    }
  }

  /**
   * Get detailed information about a specific table
   */
  async getTableDetails(tableName: string): Promise<TableDetails> {
    try {
      const response = await apiClient.get<TableDetails>(`/api/schema/tables/${tableName}`);
      return response;
    } catch (error) {
      console.error(`Failed to get table details for ${tableName}:`, error);
      throw error;
    }
  }

  /**
   * Get all available API endpoints
   */
  async getAPIEndpoints(): Promise<APIInfo> {
    try {
      const response = await apiClient.get<APIInfo>('/api/schema/apis');
      return response;
    } catch (error) {
      console.error('Failed to get API endpoints:', error);
      throw error;
    }
  }

  /**
   * Get database statistics
   */
  async getDatabaseStats(): Promise<DatabaseStats> {
    try {
      const response = await apiClient.get<DatabaseStats>('/api/schema/stats');
      return response;
    } catch (error) {
      console.error('Failed to get database stats:', error);
      throw error;
    }
  }

  /**
   * Get table names only
   */
  async getTableNames(): Promise<string[]> {
    try {
      const schema = await this.getDatabaseSchema();
      return Object.keys(schema.tables);
    } catch (error) {
      console.error('Failed to get table names:', error);
      throw error;
    }
  }

  /**
   * Get tables with basic info (name and row count)
   */
  async getTablesSummary(): Promise<Array<{ name: string; row_count: number }>> {
    try {
      const stats = await this.getDatabaseStats();
      return Object.entries(stats.tables).map(([name, info]) => ({
        name,
        row_count: info.row_count
      }));
    } catch (error) {
      console.error('Failed to get tables summary:', error);
      throw error;
    }
  }

  /**
   * Get API endpoints grouped by category
   */
  async getAPIEndpointsByCategory(): Promise<Record<string, APIEndpoint[]>> {
    try {
      const apiInfo = await this.getAPIEndpoints();
      const grouped: Record<string, APIEndpoint[]> = {};
      
      Object.entries(apiInfo).forEach(([category, group]) => {
        grouped[category] = group.endpoints;
      });
      
      return grouped;
    } catch (error) {
      console.error('Failed to get API endpoints by category:', error);
      throw error;
    }
  }

  /**
   * Get all API endpoints as a flat list
   */
  async getAllAPIEndpoints(): Promise<APIEndpoint[]> {
    try {
      const apiInfo = await this.getAPIEndpoints();
      const allEndpoints: APIEndpoint[] = [];
      
      Object.values(apiInfo).forEach(group => {
        allEndpoints.push(...group.endpoints);
      });
      
      return allEndpoints;
    } catch (error) {
      console.error('Failed to get all API endpoints:', error);
      throw error;
    }
  }

  /**
   * Get endpoints that require authentication
   */
  async getAuthenticatedEndpoints(): Promise<APIEndpoint[]> {
    try {
      const allEndpoints = await this.getAllAPIEndpoints();
      return allEndpoints.filter(endpoint => endpoint.requires_auth);
    } catch (error) {
      console.error('Failed to get authenticated endpoints:', error);
      throw error;
    }
  }

  /**
   * Get public endpoints (no authentication required)
   */
  async getPublicEndpoints(): Promise<APIEndpoint[]> {
    try {
      const allEndpoints = await this.getAllAPIEndpoints();
      return allEndpoints.filter(endpoint => !endpoint.requires_auth);
    } catch (error) {
      console.error('Failed to get public endpoints:', error);
      throw error;
    }
  }
}

export const schemaService = new SchemaService();
export default schemaService;
