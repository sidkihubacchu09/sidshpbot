const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static('public')); // Serves your HTML file

// --- CONFIGURATION ---
const OWNER_ID = 123456789; // REPLACE with your Telegram ID
const UPI_ID = "yourname@upi"; // REPLACE with your UPI ID

let db = {
    users: {}, 
    market: [
        { id: 1, title: "Premium ID #001", price: 25, image: "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=400", sellerId: "admin" },
        { id: 2, title: "Rare Username @Sid", price: 150, image: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=400", sellerId: "admin" }
    ],
    deposits: []
};

// Auth & Init
app.post('/api/init', (req, res) => {
    const { id, username } = req.body;
    if (!db.users[id]) db.users[id] = { balance: 0.00, username: username || "Customer" };
    res.json({ 
        user: db.users[id], 
        market: db.market, 
        isOwner: parseInt(id) === OWNER_ID,
        upi: UPI_ID
    });
});

// UPI Deposit Request
app.post('/api/deposit', (req, res) => {
    const { userId, amount, utr, username } = req.body;
    db.deposits.push({ id: Date.now(), userId, username, amount: parseFloat(amount), utr, status: 'pending' });
    res.json({ success: true });
});

// Buy Logic
app.post('/api/buy', (req, res) => {
    const { buyerId, itemId } = req.body;
    const item = db.market.find(i => i.id === itemId);
    if (item && db.users[buyerId].balance >= item.price) {
        db.users[buyerId].balance -= item.price;
        db.market = db.market.filter(i => i.id !== itemId);
        res.json({ success: true, balance: db.users[buyerId].balance });
    } else {
        res.status(400).json({ error: "Insufficient Funds" });
    }
});

// Sell Logic
app.post('/api/sell', (req, res) => {
    const { sellerId, title, price, image } = req.body;
    db.market.push({ id: Date.now(), title, price: parseFloat(price), image, sellerId });
    res.json({ success: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Sid Store running on port ${PORT}`));
