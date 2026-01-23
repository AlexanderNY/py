import { useState, FormEvent, useEffect, useMemo } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { testService } from '@/services/test-service'
import { useAuth } from '@/contexts/auth-context'
import type { Product } from '@/types/test'

export function TestPage() {
  const { user } = useAuth()
  const [login, setLogin] = useState(user?.username || '')
  const [orderNumber, setOrderNumber] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [products, setProducts] = useState<Product[]>([])
  const [selectedProductIds, setSelectedProductIds] = useState<Set<number>>(new Set())
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProducts, setIsLoadingProducts] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Загружаем список продуктов при монтировании
  useEffect(() => {
    async function loadProducts() {
      setIsLoadingProducts(true)
      try {
        const productsList = await testService.getProducts()
        setProducts(productsList)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load products')
      } finally {
        setIsLoadingProducts(false)
      }
    }
    loadProducts()
  }, [])

  // Обновляем login при изменении user
  useEffect(() => {
    if (user?.username) {
      setLogin(user.username)
    }
  }, [user])

  // Фильтруем продукты по поисковому запросу
  const filteredProducts = useMemo(() => {
    if (!searchQuery.trim()) {
      return products
    }
    const query = searchQuery.toLowerCase()
    return products.filter(product =>
      product.product_description.toLowerCase().includes(query)
    )
  }, [products, searchQuery])

  // Получаем выбранные продукты для отображения тегов
  const selectedProducts = useMemo(() => {
    return products.filter(p => selectedProductIds.has(p.product_id))
  }, [products, selectedProductIds])

  function handleProductToggle(productId: number) {
    setSelectedProductIds(prev => {
      const newSet = new Set(prev)
      if (newSet.has(productId)) {
        newSet.delete(productId)
      } else {
        newSet.add(productId)
      }
      return newSet
    })
  }

  function handleRemoveTag(productId: number) {
    setSelectedProductIds(prev => {
      const newSet = new Set(prev)
      newSet.delete(productId)
      return newSet
    })
  }

  async function handleSearch(e: FormEvent) {
    e.preventDefault()
    if (!orderNumber.trim()) {
      return
    }

    setError('')
    setSuccess('')
    setIsLoading(true)

    try {
      const result = await testService.searchOrder(orderNumber.trim())
      setLogin(result.login)
      setSelectedProductIds(new Set(result.product_ids))
      setSuccess('Order found and loaded successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search order')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (selectedProductIds.size === 0) {
      setError('Please select at least one product')
      return
    }

    setError('')
    setSuccess('')
    setIsLoading(true)

    try {
      const result = await testService.submitTest({
        login: login.trim(),
        product_ids: Array.from(selectedProductIds)
      })
      setSuccess(`Order created successfully! Order ID: ${result.order_id}`)
      setOrderNumber('')
      setSelectedProductIds(new Set())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit order')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Test</h1>
        <p className="text-[var(--text-secondary)] mt-1">Create and search orders with product selection</p>
      </div>

      {error && (
        <Alert variant="error" className="animate-slide-down">
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" className="animate-slide-down">
          {success}
        </Alert>
      )}

      <Card className="animate-slide-up">
        <CardHeader>
          <CardTitle>Order Form</CardTitle>
          <CardDescription>Enter order details and select products</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Login Field */}
          <div>
            <Input
              label="Login"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder="Enter login"
            />
          </div>

          {/* Order Number Field */}
          <div>
            <Input
              label="Order Number"
              value={orderNumber}
              onChange={(e) => setOrderNumber(e.target.value)}
              placeholder="Enter order number"
            />
          </div>

          {/* Selected Products Tags */}
          {selectedProducts.length > 0 && (
            <div className="flex flex-wrap gap-2 p-3 bg-[var(--bg-tertiary)] rounded-xl border border-[var(--border-color)]">
              {selectedProducts.map(product => (
                <div
                  key={product.product_id}
                  className="inline-flex items-center gap-2 px-3 py-1.5 bg-yellow-400/20 text-yellow-600 dark:text-yellow-400 rounded-lg border border-yellow-400/30"
                >
                  <span className="text-sm font-medium">{product.product_description}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(product.product_id)}
                    className="text-red-500 hover:text-red-700 transition-colors"
                    aria-label={`Remove ${product.product_description}`}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Product Selector */}
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 bg-[var(--bg-tertiary)] rounded-t-xl border border-[var(--border-color)] border-b-0">
              <label className="text-sm font-medium text-[var(--text-primary)]">Selector</label>
              <div className="relative flex-1 max-w-xs ml-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search products..."
                  className="w-full px-3 py-1.5 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                />
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
            
            <div className="max-h-64 overflow-y-auto bg-blue-50 dark:bg-blue-900/20 rounded-b-xl border border-[var(--border-color)] border-t-0 p-3 space-y-2">
              {isLoadingProducts ? (
                <div className="text-center py-8 text-[var(--text-muted)]">Loading products...</div>
              ) : filteredProducts.length === 0 ? (
                <div className="text-center py-8 text-[var(--text-muted)]">No products found</div>
              ) : (
                filteredProducts.map(product => {
                  const isSelected = selectedProductIds.has(product.product_id)
                  return (
                    <label
                      key={product.product_id}
                      className="flex items-center gap-3 p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg cursor-pointer hover:bg-orange-200 dark:hover:bg-orange-900/30 transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleProductToggle(product.product_id)}
                        className="w-4 h-4 text-primary-500 rounded focus:ring-primary-500 focus:ring-2"
                      />
                      <span className="flex-1 text-sm text-[var(--text-primary)]">
                        {product.product_description}
                      </span>
                      {isSelected && (
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-5 w-5 text-green-500"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </label>
                  )
                })
              )}
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex gap-4">
          <Button
            type="button"
            onClick={handleSearch}
            disabled={!orderNumber.trim() || isLoading}
            variant="primary"
            className="flex-1"
          >
            Search
          </Button>
          <Button
            type="button"
            onClick={handleSubmit}
            disabled={selectedProductIds.size === 0 || isLoading}
            variant="primary"
            className="flex-1"
          >
            Submit
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
