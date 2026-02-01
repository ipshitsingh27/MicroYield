#![no_std]

use soroban_sdk::{
    contract, contractimpl, contracttype,
    symbol_short, Env, Address,
};

#[contract]
pub struct Vault;

#[contracttype]
#[derive(Clone)]
pub enum DataKey {
    Admin,
    XlmBalance(Address),
    UsdcPrincipal(Address),
    UsdcYield(Address),
    TotalXlm,
    TotalUsdcPrincipal,
}


#[contractimpl]
impl Vault {

    pub fn initialize(env: Env, admin: Address) {
        if env.storage().persistent().has(&DataKey::Admin) {
            panic!("Already initialized");
        }

        env.storage().persistent().set(&DataKey::Admin, &admin);
    }

    fn require_admin(env: &Env) {
        let admin: Address = env.storage()
            .persistent()
            .get(&DataKey::Admin)
            .expect("Admin not set");

        admin.require_auth();
    }

    // ==============================
    // 1️⃣ Deposit XLM Savings
    // ==============================
    pub fn deposit_xlm(env: Env, user: Address, amount: i128) {
        user.require_auth();

        if amount <= 0 {
            panic!("Invalid deposit amount");
        }

        let key = DataKey::XlmBalance(user.clone());
        let current: i128 = env.storage().persistent().get(&key).unwrap_or(0);

        let new_balance = current.checked_add(amount).expect("Overflow");
        env.storage().persistent().set(&key, &new_balance);

        let total: i128 = env.storage().persistent().get(&DataKey::TotalXlm).unwrap_or(0);
        let new_total = total.checked_add(amount).expect("Overflow");
        env.storage().persistent().set(&DataKey::TotalXlm, &new_total);

        env.events().publish((symbol_short!("deposit_xlm"), user), amount);
    }

    // ==============================
    // 2️⃣ Invest XLM into USDC
    // ==============================
    pub fn invest_usdc(env: Env, user: Address, amount: i128) {
        user.require_auth();

        if amount <= 0 {
            panic!("Invalid invest amount");
        }

        // Reduce XLM balance
        let xlm_key = DataKey::XlmBalance(user.clone());
        let xlm_current: i128 = env.storage().persistent().get(&xlm_key).unwrap_or(0);

        if xlm_current < amount {
            panic!("Insufficient XLM balance");
        }

        let new_xlm = xlm_current.checked_sub(amount).expect("Underflow");
        env.storage().persistent().set(&xlm_key, &new_xlm);

        // Increase USDC principal
        let usdc_key = DataKey::UsdcPrincipal(user.clone());
        let usdc_current: i128 = env.storage().persistent().get(&usdc_key).unwrap_or(0);

        let new_usdc = usdc_current.checked_add(amount).expect("Overflow");
        env.storage().persistent().set(&usdc_key, &new_usdc);

        let total_usdc: i128 = env.storage().persistent().get(&DataKey::TotalUsdcPrincipal).unwrap_or(0);
        let new_total_usdc = total_usdc.checked_add(amount).expect("Overflow");
        env.storage().persistent().set(&DataKey::TotalUsdcPrincipal, &new_total_usdc);

        env.events().publish((symbol_short!("invest"), user), amount);
    }

    // ==============================
    // 3️⃣ Add Yield (Admin Controlled Later)
    // ==============================
    pub fn add_yield(env: Env, user: Address, amount: i128) {
        Self::require_admin(&env);

        if amount <= 0 {
            panic!("Invalid yield amount");
        }

        let key = DataKey::UsdcYield(user.clone());
        let current: i128 = env.storage().persistent().get(&key).unwrap_or(0);

        let new_yield = current.checked_add(amount).expect("Overflow");
        env.storage().persistent().set(&key, &new_yield);

        env.events().publish((symbol_short!("yield"), user), amount);
    }

    // ==============================
    // 4️⃣ Withdraw XLM Savings
    // ==============================
    pub fn withdraw_xlm(env: Env, user: Address, amount: i128) {
        user.require_auth();

        if amount <= 0 {
            panic!("Invalid withdraw amount");
        }

        let key = DataKey::XlmBalance(user.clone());
        let current: i128 = env.storage().persistent().get(&key).unwrap_or(0);

        if current < amount {
            panic!("Insufficient balance");
        }

        let new_balance = current.checked_sub(amount).expect("Underflow");
        env.storage().persistent().set(&key, &new_balance);

        let total: i128 = env.storage().persistent().get(&DataKey::TotalXlm).unwrap_or(0);
        let new_total = total.checked_sub(amount).expect("Underflow");
        env.storage().persistent().set(&DataKey::TotalXlm, &new_total);

        env.events().publish((symbol_short!("withdraw_xlm"), user), amount);
    }

    // ==============================
    // 5️⃣ View User Summary
    // ==============================
    pub fn get_user_summary(env: Env, user: Address) -> (i128, i128, i128) {
        let xlm = env.storage()
            .persistent()
            .get(&DataKey::XlmBalance(user.clone()))
            .unwrap_or(0);

        let principal = env.storage()
            .persistent()
            .get(&DataKey::UsdcPrincipal(user.clone()))
            .unwrap_or(0);

        let yield_amt = env.storage()
            .persistent()
            .get(&DataKey::UsdcYield(user))
            .unwrap_or(0);

        (xlm, principal, yield_amt)
    }

    // ==============================
    // 6️⃣ Global Totals
    // ==============================
    pub fn total_xlm(env: Env) -> i128 {
        env.storage()
            .persistent()
            .get(&DataKey::TotalXlm)
            .unwrap_or(0)
    }

    pub fn total_usdc_principal(env: Env) -> i128 {
        env.storage()
            .persistent()
            .get(&DataKey::TotalUsdcPrincipal)
            .unwrap_or(0)
    }
}
