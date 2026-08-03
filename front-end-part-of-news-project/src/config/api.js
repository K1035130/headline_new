/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}

// AI 问答走自己的后端代理：API Key 只存在于 Backend/.env，
// 既不会进入版本控制，也不会随打包产物发到浏览器
export const aiChatConfig = {
  apiEndpoint: `${apiConfig.baseURL}/api/ai/chat`
}
