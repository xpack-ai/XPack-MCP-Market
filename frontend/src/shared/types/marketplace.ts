export interface ServiceData {
  name: string;
  service_id: string;
  tools: ToolData[];
  long_description?: string;
  short_description?: string;
  slug_name?: string;
  tags?: string[];
  price?: string;
  charge_type?: ChargeType;
  input_token_price?: string;
  output_token_price?: string;
}

export interface ToolData {
  name: string;
  description?: string;
}

export enum ChargeType {
  Free = "free",
  PerCall = "per_call",
  PerToken = "per_token",
}
