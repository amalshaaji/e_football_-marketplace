import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { SiteLayout } from './components/SiteLayout.jsx'
import HomePage from './pages/HomePage.jsx'
import MarketplacePage from './pages/MarketplacePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import ListingDetailsPage from './pages/ListingDetailsPage.jsx'
import BuyerDashboardPage from './pages/BuyerDashboardPage.jsx'
import SellerDashboardPage from './pages/SellerDashboardPage.jsx'
import AdminDashboardPage from './pages/AdminDashboardPage.jsx'
import BuyerOrderDetailPage from './pages/BuyerOrderDetailPage.jsx'
import MessagesPage from './pages/MessagesPage.jsx'
import './App.css'

export default function App() {
  return <BrowserRouter><Routes><Route element={<SiteLayout />}>
    <Route path="/" element={<HomePage />} />
    <Route path="/marketplace" element={<MarketplacePage />} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route path="/listings/:listingId" element={<ListingDetailsPage />} />
    <Route path="/dashboard/buyer" element={<BuyerDashboardPage />} />
    <Route path="/dashboard/buyer/orders/:orderId" element={<BuyerOrderDetailPage />} />
    <Route path="/dashboard/seller" element={<SellerDashboardPage />} />
    <Route path="/dashboard/admin" element={<AdminDashboardPage />} />
    <Route path="/messages" element={<MessagesPage />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Route></Routes></BrowserRouter>
}
