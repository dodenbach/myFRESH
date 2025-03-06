import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import ProductCard from '../components/marketplace/ProductCard'
import FilterBar from '../components/marketplace/FilterBar'

export default function Home() {
  const [products, setProducts] = useState([])
  const [cart, setCart] = useState([])

  useEffect(() => {
    supabase.from('products').select('*').then(({ data }) => setProducts(data))
  }, [])

  const handleFilter = ({ category, priceRange }) => {
    supabase
      .from('products')
      .select('*')
      .ilike('category', `%${category}%`)
      .gte('price', priceRange[0])
      .lte('price', priceRange[1])
      .then(({ data }) => setProducts(data))
  }

  const addToCart = (product) => {
    setCart([...cart, { ...product, quantity: 1 }])
  }

  return (
    <div>
      <h1>Marketplace</h1>
      <FilterBar onFilter={handleFilter} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)' }}>
        {products.map(product => (
          <ProductCard key={product.id} product={product} onAddToCart={addToCart} />
        ))}
      </div>
    </div>
  )
}
