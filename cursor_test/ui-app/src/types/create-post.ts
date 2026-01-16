export interface CreatePostRequest {
  social_networks: {
    tg?: boolean
    tw?: boolean
    vk?: boolean
    wp?: boolean
  }
  text: string
}
