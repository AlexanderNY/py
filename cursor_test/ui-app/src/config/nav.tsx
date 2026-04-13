import type { ComponentType } from 'react'
import {
  UserIcon,
  LineChartIcon,
  TelegramIcon,
  ThreadsIcon,
  WordPressIcon,
  TwitterIcon,
  VKontakteIcon,
  InstagramIcon,
  LinkIcon,
  PlusIcon,
  ClipboardListIcon,
  SettingsIcon,
  UserGroupIcon,
  DocumentTextIcon,
} from '@/components/icons'

export interface NavItem {
  path: string
  label: string
  Icon: ComponentType<{ className?: string }>
}

export const navItems: NavItem[] = [
  { path: '/profile', label: 'Profile', Icon: UserIcon },
  { path: '/graphs', label: 'Graphs', Icon: LineChartIcon },
  { path: '/telegram', label: 'Telegram', Icon: TelegramIcon },
  { path: '/threads', label: 'Threads', Icon: ThreadsIcon },
  { path: '/wordpress', label: 'WordPress', Icon: WordPressIcon },
  { path: '/twitter', label: 'Twitter', Icon: TwitterIcon },
  { path: '/vkontakte', label: 'VKontakte', Icon: VKontakteIcon },
  { path: '/instagram', label: 'Instagram', Icon: InstagramIcon },
  { path: '/dzen', label: 'Дзен', Icon: DocumentTextIcon },
  { path: '/custom-url', label: 'Custom URL', Icon: LinkIcon },
  { path: '/posts', label: 'Posts', Icon: PlusIcon },
  { path: '/test', label: 'Test', Icon: ClipboardListIcon },
]

export const groupNavItem: NavItem = {
  path: '/group',
  label: 'My group',
  Icon: UserGroupIcon,
}

export const adminNavItems: NavItem[] = [
  { path: '/administration', label: 'Administration', Icon: SettingsIcon },
]
