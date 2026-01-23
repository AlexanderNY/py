export interface Product {
  product_id: number
  product_description: string
}

export interface SearchResponse {
  order_id: string
  login: string
  product_ids: number[]
}

export interface SubmitRequest {
  login: string
  product_ids: number[]
}

export interface SubmitResponse {
  message: string
  order_id: string
}
