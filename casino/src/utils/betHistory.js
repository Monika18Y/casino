import { betApi } from './api'

// 获取投注记录
export const getBetHistory = async () => {
  try {
    // 调用API获取投注记录
    const response = await betApi.getBetRecords()
    return response.data
  } catch (error) {
    console.error('获取投注记录失败:', error)
    return []
  }
}

// 添加投注记录
export const addBetHistory = async (record) => {
  try {
    // 确保必要字段存在且格式正确
    const betData = {
      game: record.game || 'Unknown',
      bet_amount: parseFloat(record.bet_amount || 0).toFixed(2),
      profit: parseFloat(record.profit || 0).toFixed(2),
      game_details: record.game_details || {}
    }
    
    // 调用API添加投注记录
    const response = await betApi.createBetRecord(betData)
    return response.data
  } catch (error) {
    console.error('存储游戏记录失败:', error)
    if (error.response && error.response.data) {
      console.error('错误详情:', error.response.data)
    }
    return false
  }
} 