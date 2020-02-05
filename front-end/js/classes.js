var currencies = [];
var companies = [];
var products = [];
var trades = [];

class Trade {
    constructor(id) {
        this.tradeId = id;
        this.tradeDate = new Date();
        this.userIdCreatedBy = 0;
        this.lastModifiedDate = new Date();
        this.product = null; // a Product object
        this.buyingParty = null; // a Company object
        this.sellingParty = null; // a Company object
        this.quantity = 0;
        this.notionalPrice = "";
        this.notionalCurrency = "";
        this.underlyingPrice = "";
        this.underlyingCurrency = "";
        this.maturityDate = new Date();
        this.strikePrice = "";
    }

    getNotionalCurrencyObject() {
        return getCurrencyList().filter((x) => { x.code == this.notionalCurrency })[0];
    }

    getUnderlyingCurrencyObject() {
        return getCurrencyList().filter((x) => { x.code == this.underlyingCurrency })[0];
    }

    getAPIObject() {
        let a = new APITrade();
        a.product = this.product.id;
        a.buyingParty = this.buyingParty.id;
        a.sellingParty = this.sellingParty.id;
        a.quantity = this.quantity;
        a.notionalPrice = this.notionalPrice;
        a.notionalCurrency = this.notionalCurrency;
        a.underlyingPrice = this.underlyingPrice;
        a.underlyingCurrency = this.underlyingCurrency;
        a.maturityDate = this.maturityDate.toISOString();
        a.strikePrice = this.strikePrice;
        return a;
    }

    populateFromServerJSON(o) {
        // TODO whole function needs error handling
        this.tradeId = o.tradeId;
        this.tradeDate = new Date(o.tradeDate);
        this.userIdCreatedBy = o.userIdCreatedBy;
        this.lastModifiedDate = new Date(o.lastModifiedDate);

        //  TODO possibly better ways to do this...
        let products = getProductList(this.tradeDate);
        this.product = products.filter(p => p.id === o.product)[0];
        let companies = getCompanyList(this.tradeDate);
        this.buyingParty = companies.filter(c => c.id === o.buyingParty)[0];
        this.sellingParty = companies.filter(c => c.id === o.sellingParty)[0];

        this.quantity = o.quantity;
        this.notionalPrice = o.notionalPrice;
        this.notionalCurrency = o.notionalCurrency;
        this.underlyingPrice = o.underlyingPrice;
        this.underlyingCurrency = o.underlyingCurrency;
        this.maturityDate = new Date(o.maturityDate);
        this.strikePrice = o.strikePrice;
        return this;
    }
};

class APITrade {
    constructor() {
        this.product = "";
        this.buyingParty = "";
        this.sellingParty = "";
        this.quantity = 0;
        this.notionalPrice = "";
        this.notionalCurrency = "";
        this.underlyingPrice = "";
        this.underlyingCurrency = "";
        this.maturityDate = "";
        this.strikePrice = "";
    }
}

function * tradeGenerator(e) {
    let x = 0;
    while(true) {
        let t = new Trade();
        t.tradeId = e ? "NEW " + x++ : randInt(0, 999999999).toString().padStart(9, "0");
        t.tradeDate = new Date();
        t.userIdCreatedBy = randInt(0,9999999);
        t.lastModifiedDate = randDate();
        t.product = randProductString();
        t.buyingParty = randCompanyString();
        t.sellingParty = randCompanyString();
        t.quantity = randInt(0, 100);
        let c1 = randCurrency();
        let c2 = randCurrency();
        t.notionalCurrency = c1.code;
        t.notionalPrice = randCurrencyString(c1);
        t.underlyingCurrency = c2.code;
        t.underlyingPrice = randCurrencyString(c2);
        t.maturityDate = randDate();
        t.strikePrice = randCurrencyString(c2);
        yield t;
    }
};

function getTradeList() {
    if (trades.length == 0) {
        for (let i = 0; i < 10; i++) {
            trades.push(tradeGenerator(false).next().value);
        }
    }
    return trades;
};

class Product {
    constructor() {
        this.id = "";
        this.name = "";
        this.companyId = "";
        this.value = 0;
        this.creationDate = new Date();
        this.userIdCreatedBy = 0;
    }

	getAPIObject() {
		let a = new APIProduct();
		a.id = this.id;
		a.value = this.value;
		a.company = this.companyId;
		return a;
	}
};

class APIProduct {
	constructor() {
		this.id = "";
		this.value = "";
		this.company = "";
	}
}


function * productGenerator() {
    while (true) {
        let p = new Product();
        p.id = randInt(0, 999).toString();
        p.name = "Product " + p.id;
        p.companyId = randInt(0, 999999).toString();
        p.value = (randInt(0,9999) + Math.random()).toFixed(2);
        p.creatioDate = randDate();
        p.userIdCreatedBy = randInt(0, 999999);
        yield p;
    }
};

function getProductList(date) {
    if (products.length == 0) {
        for (let i = 0; i < 10; i++) {
            products.push(productGenerator().next().value);
        }
    }
    return products;
}

class Currency {
    constructor(code, sym, decimal, val) {
        this.code = code;
        this.symbol = sym;
        this.allowDecimal = decimal;
        this.value = val;
    }
};

function getCurrencyList() {
    if (currencies.length == 0) {
        currencyData.forEach((c) => {
            currencies.push(new Currency(c[0], c[1], c[2], c[3]));
        });
    }
    return currencies;
}

//the ten global most traded currencies
const currencyData = [
    ["USD", "$", true, 1],
    ["EUR", "€", true, 1],
    ["JPY", "¥", false, 1],
    ["GPB", "£", true, 1],
    ["AUD", "$", true, 1],
    ["CAD", "$", true, 1],
    ["CHF", "CHF", true, 1],
    ["CNY", "元", true, 1],
    ["HKD", "$", true, 1],
    ["NZD", "$", true, 1]
];

class Company {
    constructor() {
        this.id = "";
        this.name = "";
        this.foundedDate = new Date();
        this.creationDate = new Date();
        this.userIdCreatedBy = 0;
    }

	getAPIObject() {
		let c = new APICompany();
		c.id = this.id;
		c.foundedDate = this.foundedDate;
		return c;
	}
};

class APICompany {
	constructor() {
		this.name = "";
		this.foundedDate = "";
	}
}


function * companyGenerator() {
    while (true) {
        let c = new Company();
        c.id = randInt(0, 999).toString();
        c.name = "Company " + c.id;
        c.foundedDate = randDate();
        c.creationDate = randDate();
        c.userIdCreatedBy = randInt(0, 999999);
        yield c;
    }
}

function getCompanyList(date) {
    if (companies.length == 0) {
        for (let i = 0; i < 10; i++) {
            companies.push(companyGenerator().next().value);
        }
    }
    return companies;
}
