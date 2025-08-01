"use client";

import { useState, useCallback } from "react";
import { MCPService } from "@/types/mcp-service";
import {
  getMCPServiceDetail,
  parseOpenAPIDocumentForUpdate as parseOpenAPIDocumentForUpdateAPI,
} from "@/services/mcpService";

export const useMCPServiceDetail = () => {
  const [serviceDetail, setServiceDetail] = useState<MCPService | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);

  // get service detail
  const getServiceDetail = useCallback(
    async (serviceId: string): Promise<MCPService | null> => {
      setDetailLoading(true);
      setDetailError(null);

      try {
        const response = await getMCPServiceDetail({ id: serviceId });

        if (response.success && response.data) {
          setServiceDetail(response.data);
          return response.data;
        } else {
          setDetailError(
            response.error_message || "Failed to load service detail"
          );
          setServiceDetail(null);
          return null;
        }
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load service detail";
        setDetailError(errorMessage);
        setServiceDetail(null);
        console.error("Get service detail error:", err);
        return null;
      } finally {
        setDetailLoading(false);
      }
    },
    []
  );

  // clear service detail
  const clearServiceDetail = useCallback(() => {
    setServiceDetail(null);
    setDetailError(null);
  }, []);

  // parse OpenAPI document for update
  const parseOpenAPIDocumentForUpdate = useCallback(
    async (
      serviceId: string,
      url?: string,
      file?: File
    ): Promise<MCPService> => {
      setUpdateLoading(true);
      setUpdateError(null);

      try {
        const response = await parseOpenAPIDocumentForUpdateAPI({
          id: serviceId,
          file,
          url,
        });

        if (response.success && response.data) {
          // Update the service detail with the new data
          setServiceDetail(response.data);
          return response.data;
        } else {
          throw new Error(
            response.error_message ||
              "Failed to parse OpenAPI document for update"
          );
        }
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to parse OpenAPI document for update";
        setUpdateError(errorMessage);
        throw err;
      } finally {
        setUpdateLoading(false);
      }
    },
    []
  );

  return {
    serviceDetail,
    detailLoading,
    detailError,
    updateLoading,
    updateError,
    getServiceDetail,
    clearServiceDetail,
    parseOpenAPIDocumentForUpdate,
  };
};
