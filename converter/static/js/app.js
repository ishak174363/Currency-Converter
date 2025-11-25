// Currency Converter App JavaScript

// DOM Elements
const amountInput = document.getElementById('amount');
const fromCurrencySelect = document.getElementById('fromCurrency');
const toCurrencySelect = document.getElementById('toCurrency');
const convertBtn = document.getElementById('convertBtn');
const swapBtn = document.getElementById('swapBtn');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');
const convertBtnText = document.getElementById('convertBtnText');
const convertBtnLoading = document.getElementById('convertBtnLoading');

// State
let currencies = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadCurrencies();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    convertBtn.addEventListener('click', handleConvert);
    swapBtn.addEventListener('click', handleSwap);

    // Allow Enter key to trigger conversion
    amountInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleConvert();
        }
    });
}

// Load available currencies
async function loadCurrencies() {
    try {
        const response = await fetch('/currencies/');

        if (!response.ok) {
            throw new Error('Failed to load currencies');
        }

        currencies = await response.json();
        populateCurrencySelects();

    } catch (error) {
        console.error('Error loading currencies:', error);
        showError('Failed to load currencies. Please refresh the page.');
    }
}

// Populate currency select dropdowns
function populateCurrencySelects() {
    // Clear existing options except the first one
    fromCurrencySelect.innerHTML = '<option value="">Select currency...</option>';
    toCurrencySelect.innerHTML = '<option value="">Select currency...</option>';

    // Add currency options
    currencies.forEach(currency => {
        const optionFrom = document.createElement('option');
        optionFrom.value = currency.code;
        optionFrom.textContent = `${currency.code} - ${currency.name}`;
        fromCurrencySelect.appendChild(optionFrom);

        const optionTo = document.createElement('option');
        optionTo.value = currency.code;
        optionTo.textContent = `${currency.code} - ${currency.name}`;
        toCurrencySelect.appendChild(optionTo);
    });

    // Set default values
    fromCurrencySelect.value = 'USD';
    toCurrencySelect.value = 'EUR';
}

// Handle currency conversion
async function handleConvert() {
    // Hide previous results/errors
    hideResult();
    hideError();

    // Validate inputs
    const amount = parseFloat(amountInput.value);
    const fromCurrency = fromCurrencySelect.value;
    const toCurrency = toCurrencySelect.value;

    if (!amount || amount <= 0) {
        showError('Please enter a valid amount greater than 0');
        return;
    }

    if (!fromCurrency) {
        showError('Please select a currency to convert from');
        return;
    }

    if (!toCurrency) {
        showError('Please select a currency to convert to');
        return;
    }

    // Show loading state
    setLoading(true);

    try {
        const response = await fetch('/conversions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                from_currency: fromCurrency,
                to_currency: toCurrency,
                amount: amount
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Conversion failed');
        }

        displayResult(data);

    } catch (error) {
        console.error('Conversion error:', error);
        showError(error.message || 'Failed to convert currency. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Handle currency swap
function handleSwap() {
    const fromValue = fromCurrencySelect.value;
    const toValue = toCurrencySelect.value;

    fromCurrencySelect.value = toValue;
    toCurrencySelect.value = fromValue;

    // Add animation effect
    swapBtn.classList.add('rotate-180');
    setTimeout(() => {
        swapBtn.classList.remove('rotate-180');
    }, 300);
}

// Display conversion result
function displayResult(data) {
    const resultAmount = document.getElementById('resultAmount');
    const resultRate = document.getElementById('resultRate');
    const resultTimestamp = document.getElementById('resultTimestamp');

    // Format numbers
    const formattedAmount = parseFloat(data.converted_amount).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const formattedRate = parseFloat(data.exchange_rate).toLocaleString('en-US', {
        minimumFractionDigits: 6,
        maximumFractionDigits: 6
    });

    // Get currency symbols
    const fromCurrencyObj = currencies.find(c => c.code === data.from_currency);
    const toCurrencyObj = currencies.find(c => c.code === data.to_currency);

    const fromSymbol = fromCurrencyObj?.symbol || data.from_currency;
    const toSymbol = toCurrencyObj?.symbol || data.to_currency;

    // Update result display
    resultAmount.textContent = `${toSymbol} ${formattedAmount} ${data.to_currency}`;
    resultRate.textContent = `1 ${data.from_currency} = ${formattedRate} ${data.to_currency}`;

    // Format timestamp
    const timestamp = new Date(data.last_updated);
    resultTimestamp.textContent = `Last updated: ${timestamp.toLocaleString()}`;

    // Show result with animation
    resultDiv.classList.remove('hidden');
    resultDiv.classList.add('animate-fadeIn');
}

// Show error message
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorDiv.classList.remove('hidden');

    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Hide error message
function hideError() {
    errorDiv.classList.add('hidden');
}

// Hide result
function hideResult() {
    resultDiv.classList.add('hidden');
}

// Set loading state
function setLoading(isLoading) {
    if (isLoading) {
        convertBtn.disabled = true;
        convertBtnText.classList.add('hidden');
        convertBtnLoading.classList.remove('hidden');
    } else {
        convertBtn.disabled = false;
        convertBtnText.classList.remove('hidden');
        convertBtnLoading.classList.add('hidden');
    }
}

// Add custom animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fadeIn {
        animation: fadeIn 0.3s ease-out;
    }
    
    .rotate-180 {
        transform: rotate(180deg);
        transition: transform 0.3s ease-in-out;
    }
`;
document.head.appendChild(style);
