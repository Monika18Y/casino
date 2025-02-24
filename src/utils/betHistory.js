// 获取投注记录
export const getBetHistory = () => {
  try {
    return JSON.parse(sessionStorage.getItem('betHistory') || '[]')
  } catch {
    return []
  }
}

// 添加投注记录
export const addBetHistory = (record) => {
  try {
    const history = getBetHistory()
    history.unshift({
      id: Date.now(),
      time: new Date().toLocaleTimeString(),
      ...record
    })
    // 只保留最近20条记录
    // if (history.length > 20) {
    //   history.pop()
    // }
    sessionStorage.setItem('betHistory', JSON.stringify(history))
  } catch (error) {
    console.error('存储游戏记录失败:', error)
  }
} 