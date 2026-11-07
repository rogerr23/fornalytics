export type Category = 'cozinha' | 'decoracao' | 'banho' | 'quarto'

export interface Product {
  id: string
  name: string
  description: string
  category: Category
  price: number
  stock: number
}
