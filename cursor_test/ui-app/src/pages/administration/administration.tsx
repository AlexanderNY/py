import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { authService } from '@/services/auth-service'
import { coreService } from '@/services/core-service'
import type { User } from '@/types/auth'
import type { UserStatisticsItem, ScheduleSnapshot } from '@/types/core'

export function AdministrationPage() {
  const [activeTab, setActiveTab] = useState<'users' | 'statistics' | 'schedule'>('users')
  const [users, setUsers] = useState<User[]>([])
  const [statistics, setStatistics] = useState<UserStatisticsItem[]>([])
  const [schedules, setSchedules] = useState<ScheduleSnapshot[]>([])
  const [isLoadingUsers, setIsLoadingUsers] = useState(false)
  const [isLoadingStatistics, setIsLoadingStatistics] = useState(false)
  const [isLoadingSchedule, setIsLoadingSchedule] = useState(false)
  const [isStartingDiscovery, setIsStartingDiscovery] = useState(false)
  const [isStartingBot, setIsStartingBot] = useState(false)
  const [usersError, setUsersError] = useState('')
  const [statisticsError, setStatisticsError] = useState('')
  const [scheduleError, setScheduleError] = useState('')
  const [discoveryMessage, setDiscoveryMessage] = useState('')
  const [botMessage, setBotMessage] = useState('')
  const [selectedBots, setSelectedBots] = useState<{ [key: string]: boolean }>({
    wp: false,
    tg: false,
    tw: false,
    vk: false
  })

  async function handleLoadUsers() {
    setUsersError('')
    setIsLoadingUsers(true)
    try {
      const data = await authService.getUsers()
      setUsers(data)
    } catch (error) {
      setUsersError(error instanceof Error ? error.message : 'Failed to fetch users')
      setUsers([])
    } finally {
      setIsLoadingUsers(false)
    }
  }

  async function handleLoadStatistics() {
    setStatisticsError('')
    setIsLoadingStatistics(true)
    try {
      const response = await coreService.getUsersStatistics()
      setStatistics(response.users || [])
    } catch (error) {
      setStatisticsError(error instanceof Error ? error.message : 'Failed to fetch statistics')
      setStatistics([])
    } finally {
      setIsLoadingStatistics(false)
    }
  }

  async function handleLoadSchedule() {
    setScheduleError('')
    setIsLoadingSchedule(true)
    try {
      const response = await coreService.getSchedule()
      setSchedules(response.schedules || [])
    } catch (error) {
      setScheduleError(error instanceof Error ? error.message : 'Failed to fetch schedule')
      setSchedules([])
    } finally {
      setIsLoadingSchedule(false)
    }
  }

  async function handleStartDiscovery() {
    setDiscoveryMessage('')
    setScheduleError('')
    setIsStartingDiscovery(true)
    try {
      const response = await coreService.startDiscovery()
      setDiscoveryMessage(response.message + (response.changed ? ' (Changes detected)' : ' (No changes)'))
    } catch (error) {
      setScheduleError(error instanceof Error ? error.message : 'Failed to start discovery')
      setDiscoveryMessage('')
    } finally {
      setIsStartingDiscovery(false)
    }
  }

  async function handleStartBot() {
    const selectedPlatforms = Object.entries(selectedBots)
      .filter(([_, selected]) => selected)
      .map(([platform]) => platform)
    
    if (selectedPlatforms.length === 0) {
      setBotMessage('Please select at least one bot')
      return
    }

    setBotMessage('')
    setScheduleError('')
    setIsStartingBot(true)
    try {
      const response = await coreService.startBot(selectedPlatforms)
      const results = Object.entries(response.results || {})
        .map(([platform, result]: [string, any]) => 
          `${platform}: ${result.status === 'success' ? 'Success' : 'Error'}`
        )
        .join(', ')
      setBotMessage(`Bots started: ${results}`)
    } catch (error) {
      setScheduleError(error instanceof Error ? error.message : 'Failed to start bots')
      setBotMessage('')
    } finally {
      setIsStartingBot(false)
    }
  }

  function handleBotToggle(platform: string) {
    setSelectedBots(prev => ({
      ...prev,
      [platform]: !prev[platform]
    }))
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Administration</h1>
        <p className="text-[var(--text-secondary)] mt-1">Manage users and view usage statistics</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 border-b border-[var(--border-color)]">
        <button
          onClick={() => setActiveTab('users')}
          className={`px-4 py-2 font-medium text-sm transition-colors ${
            activeTab === 'users'
              ? 'text-primary-400 border-b-2 border-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          Users
        </button>
        <button
          onClick={() => setActiveTab('statistics')}
          className={`px-4 py-2 font-medium text-sm transition-colors ${
            activeTab === 'statistics'
              ? 'text-primary-400 border-b-2 border-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          Statistics
        </button>
        <button
          onClick={() => setActiveTab('schedule')}
          className={`px-4 py-2 font-medium text-sm transition-colors ${
            activeTab === 'schedule'
              ? 'text-primary-400 border-b-2 border-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          Schedule
        </button>
      </div>

      {/* Users Tab */}
      {activeTab === 'users' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              Users Management
            </CardTitle>
            <CardDescription>View and manage all registered users</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={handleLoadUsers} 
              isLoading={isLoadingUsers}
              className="w-full sm:w-auto"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Load Users
            </Button>

            {usersError && (
              <Alert variant="error" className="animate-slide-down">
                {usersError}
              </Alert>
            )}

            {users.length > 0 && (
              <div className="overflow-x-auto animate-slide-down">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b border-[var(--border-color)]">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Username</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Email</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Role</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Email Verified</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Created At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr 
                        key={user.email} 
                        className="border-b border-[var(--border-color)] hover:bg-[var(--bg-secondary)] transition-colors"
                      >
                        <td className="py-3 px-4 text-[var(--text-secondary)] font-medium">{user.username}</td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">{user.email}</td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
                            user.role === 'admin'
                              ? 'bg-purple-500/20 text-purple-400'
                              : user.role === 'user'
                              ? 'bg-blue-500/20 text-blue-400'
                              : 'bg-gray-500/20 text-gray-400'
                          }`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          {user.is_email_verified ? (
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-emerald-500/20 text-emerald-400">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Verified
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-yellow-500/20 text-yellow-400">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                              Not Verified
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {users.length === 0 && !isLoadingUsers && !usersError && (
              <p className="text-[var(--text-muted)] text-center py-8">
                Click "Load Users" to fetch the list of users
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Statistics Tab */}
      {activeTab === 'statistics' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Usage Statistics
            </CardTitle>
            <CardDescription>View usage statistics for all users</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={handleLoadStatistics} 
              isLoading={isLoadingStatistics}
              className="w-full sm:w-auto"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Collect Statistics
            </Button>

            {statisticsError && (
              <Alert variant="error" className="animate-slide-down">
                {statisticsError}
              </Alert>
            )}

            {statistics.length > 0 && (
              <div className="overflow-x-auto animate-slide-down">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b border-[var(--border-color)]">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Username</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Email</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Role</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Total Posts</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Collected</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Processed</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Published</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statistics.map((stat) => (
                      <tr 
                        key={stat.user_id} 
                        className="border-b border-[var(--border-color)] hover:bg-[var(--bg-secondary)] transition-colors"
                      >
                        <td className="py-3 px-4 text-[var(--text-secondary)] font-medium">{stat.username}</td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">{stat.email}</td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
                            stat.role === 'admin'
                              ? 'bg-purple-500/20 text-purple-400'
                              : stat.role === 'user'
                              ? 'bg-blue-500/20 text-blue-400'
                              : 'bg-gray-500/20 text-gray-400'
                          }`}>
                            {stat.role}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-[var(--text-secondary)] font-medium">{stat.total_posts.toLocaleString()}</td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">{stat.collected_posts.toLocaleString()}</td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">{stat.processed_posts.toLocaleString()}</td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">{stat.published_posts.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {statistics.length === 0 && !isLoadingStatistics && !statisticsError && (
              <p className="text-[var(--text-muted)] text-center py-8">
                Click "Collect Statistics" to view usage statistics
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Schedule Tab */}
      {activeTab === 'schedule' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Schedule Snapshots
            </CardTitle>
            <CardDescription>View schedule snapshots from schedule_snapshots table</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Кнопка запуска сбора расписаний */}
            <div className="space-y-4 border-t border-[var(--border-color)] pt-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">Запуск сбора расписаний</h3>
                <p className="text-sm text-[var(--text-secondary)] mb-4">
                  Принудительно запускает один цикл сбора расписаний из core сервиса
                </p>
                <Button 
                  onClick={handleStartDiscovery} 
                  isLoading={isStartingDiscovery}
                  className="w-full sm:w-auto"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Запуск сбора расписаний
                </Button>
                {discoveryMessage && (
                  <Alert variant="success" className="mt-2 animate-slide-down">
                    {discoveryMessage}
                  </Alert>
                )}
              </div>
            </div>

            {/* Форма принудительного запуска ботов */}
            <div className="space-y-4 border-t border-[var(--border-color)] pt-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">Принудительный запуск ботов</h3>
                <p className="text-sm text-[var(--text-secondary)] mb-4">
                  Выберите ботов для запуска и нажмите кнопку запуска
                </p>
                
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                  {['wp', 'tg', 'tw', 'vk'].map((platform) => (
                    <label
                      key={platform}
                      className="flex items-center space-x-2 cursor-pointer p-3 rounded-lg border border-[var(--border-color)] hover:bg-[var(--bg-secondary)] transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={selectedBots[platform]}
                        onChange={() => handleBotToggle(platform)}
                        className="w-4 h-4 text-primary-400 rounded focus:ring-primary-400"
                      />
                      <span className="text-[var(--text-secondary)] font-medium uppercase">{platform}</span>
                    </label>
                  ))}
                </div>

                <Button 
                  onClick={handleStartBot} 
                  isLoading={isStartingBot}
                  className="w-full sm:w-auto"
                  disabled={Object.values(selectedBots).every(v => !v)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Запустить боты
                </Button>
                {botMessage && (
                  <Alert variant={botMessage.includes('Error') ? 'error' : 'success'} className="mt-2 animate-slide-down">
                    {botMessage}
                  </Alert>
                )}
              </div>
            </div>

            {/* Кнопка получения расписания */}
            <div className="space-y-4 border-t border-[var(--border-color)] pt-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">Просмотр расписаний</h3>
                <p className="text-sm text-[var(--text-secondary)] mb-4">
                  Загрузить расписания из таблицы schedule_snapshots
                </p>
                <Button 
                  onClick={handleLoadSchedule} 
                  isLoading={isLoadingSchedule}
                  className="w-full sm:w-auto"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Получить расписание
                </Button>
              </div>
            </div>

            {scheduleError && (
              <Alert variant="error" className="animate-slide-down">
                {scheduleError}
              </Alert>
            )}

            {schedules.length > 0 && (
              <div className="overflow-x-auto animate-slide-down">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b border-[var(--border-color)]">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">User ID</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Platform</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Publish Enabled</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Collect Enabled</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Schedule Type</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Time Intervals</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-primary)]">Updated At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {schedules.map((schedule, index) => (
                      <tr 
                        key={`${schedule.user_id}-${schedule.platform}-${index}`} 
                        className="border-b border-[var(--border-color)] hover:bg-[var(--bg-secondary)] transition-colors"
                      >
                        <td className="py-3 px-4 text-[var(--text-secondary)] font-medium">{schedule.user_id}</td>
                        <td className="py-3 px-4">
                          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-blue-500/20 text-blue-400">
                            {schedule.platform}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          {schedule.publish_enabled ? (
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-emerald-500/20 text-emerald-400">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Enabled
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-gray-500/20 text-gray-400">
                              Disabled
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          {schedule.collect_enabled ? (
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-emerald-500/20 text-emerald-400">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Enabled
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-gray-500/20 text-gray-400">
                              Disabled
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">{schedule.schedule_type}</td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">
                          {schedule.time_intervals && schedule.time_intervals.length > 0 ? (
                            <div className="flex flex-col gap-1">
                              {schedule.time_intervals.map((interval, idx) => (
                                <span key={idx} className="text-xs">
                                  {interval.start} - {interval.end}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-[var(--text-muted)]">No intervals</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-[var(--text-secondary)]">
                          {new Date(schedule.updated_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {schedules.length === 0 && !isLoadingSchedule && !scheduleError && (
              <p className="text-[var(--text-muted)] text-center py-8">
                Click "Получить расписание" to fetch schedule snapshots
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
