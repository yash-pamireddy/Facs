/**
 * @project Facs Spatial Biometric Engine
 * @engine Pulse AI
 * @copyright (c) 2026 Facs. All Rights Reserved.
 * Proprietary and Confidential.
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const app = express();
app.use(helmet({ contentSecurityPolicy: false }));

const verifyLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 30,
    standardHeaders: true,
    legacyHeaders: false,
    message: { success: false, error: 'Too many verification attempts. Please try again later.' }
});

app.use(express.json({ limit: '20mb' }));
app.use(cors());
app.use(express.static(path.join(__dirname, 'pages')));

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_ANON_KEY
);

// Clean Route mappings
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'pages/auth.html')));
app.get('/auth', (req, res) => res.sendFile(path.join(__dirname, 'pages/auth.html')));
app.get('/home', (req, res) => res.sendFile(path.join(__dirname, 'pages/home.html')));
app.get('/dashboard', (req, res) => res.sendFile(path.join(__dirname, 'pages/dashboard.html')));
app.get('/upgrade', (req, res) => res.sendFile(path.join(__dirname, 'pages/upgrade.html')));

app.get('/api/health', (req, res) => {
    res.status(200).json({ status: 'online', service: 'Facs Anti-Coercion Spatial Engine' });
});

// Verification Endpoint
app.post('/api/v1/verify', verifyLimiter, async (req, res) => {
    const { faceVector } = req.body;

    if (!Array.isArray(faceVector) || faceVector.length !== 1404) {
        return res.status(400).json({ success: false, error: 'Invalid 1404D biometric mesh vector structure.' });
    }

    const cleanVector = faceVector.map(Number);
    if (cleanVector.some(isNaN)) {
        return res.status(400).json({ success: false, error: 'Malformed vector payload.' });
    }

    try {
        const { data: matches, error: matchError } = await supabase.rpc('match_face', {
            query_embedding: cleanVector,
            match_threshold: 0.45,
            match_count: 1
        });

        if (matchError) console.error('Supabase RPC Match Error:', matchError);

        if (matches && matches.length > 0) {
            const matchedUserId = matches[0].user_id;
            const secureToken = Buffer.from(`facs_session_${Date.now()}_${matchedUserId}`).toString('base64');

            return res.status(200).json({
                success: true,
                isNewUser: false,
                userId: matchedUserId,
                token: secureToken
            });
        } else {
            return res.status(200).json({
                success: true,
                isNewUser: true,
                message: 'Active liveness passed. New profile registration required.'
            });
        }
    } catch (err) {
        console.error('Pipeline error:', err);
        return res.status(500).json({ success: false, error: 'Biometric verification pipeline error.' });
    }
});

// New User Registration Endpoint
app.post('/api/v1/register', verifyLimiter, async (req, res) => {
    const { userId, faceVector } = req.body;

    if (!userId || typeof userId !== 'string') {
        return res.status(400).json({ success: false, error: 'Valid username required.' });
    }

    if (!Array.isArray(faceVector) || faceVector.length !== 1404) {
        return res.status(400).json({ success: false, error: 'Invalid biometric mesh.' });
    }

    const cleanVector = faceVector.map(Number);

    try {
        const { error: insertError } = await supabase.from('facs_auth').insert([
            { user_id: userId.trim(), face_vector: cleanVector }
        ]);

        if (insertError) throw insertError;

        const secureToken = Buffer.from(`facs_session_${Date.now()}_${userId}`).toString('base64');

        return res.status(200).json({
            success: true,
            message: `Account created successfully for ${userId}.`,
            token: secureToken
        });
    } catch (err) {
        console.error('Registration error:', err);
        return res.status(500).json({ success: false, error: err.message || 'Registration failed.' });
    }
});

// Export app for Vercel Serverless environment
module.exports = app;

// Start local listener only when running locally (not in production on Vercel)
if (process.env.NODE_ENV !== 'production') {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`Facs Anti-Coercion Engine online at http://localhost:${PORT}`);
    });
}