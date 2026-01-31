#![no_std]

use soroban_sdk::{
    contract, contractimpl, contracttype,
    Env, Address,
};

#[contract]
pub struct Vault;

#[contracttype]
#[derive(Clone)]
pub enum DataKey {
    Balance(Address),
    Total,
}

#[contractimpl]
impl Vault {

    pub fn deposit(env: Env, user: Address, amount: i128) {
        user.require_auth();

        let key = DataKey::Balance(user.clone());

        let current: i128 = env
            .storage()
            .instance()
            .get(&key)
            .unwrap_or(0);

        env.storage().instance().set(&key, &(current + amount));

        let total: i128 = env
            .storage()
            .instance()
            .get(&DataKey::Total)
            .unwrap_or(0);

        env.storage().instance().set(&DataKey::Total, &(total + amount));
    }

    pub fn withdraw(env: Env, user: Address, amount: i128) {
        user.require_auth();

        let key = DataKey::Balance(user.clone());

        let current: i128 = env
            .storage()
            .instance()
            .get(&key)
            .unwrap_or(0);

        if current < amount {
            panic!("Insufficient balance");
        }

        env.storage().instance().set(&key, &(current - amount));

        let total: i128 = env
            .storage()
            .instance()
            .get(&DataKey::Total)
            .unwrap_or(0);

        env.storage().instance().set(&DataKey::Total, &(total - amount));
    }

    pub fn get_balance(env: Env, user: Address) -> i128 {
        let key = DataKey::Balance(user);
        env.storage().instance().get(&key).unwrap_or(0)
    }

    pub fn total_vault(env: Env) -> i128 {
        env.storage()
            .instance()
            .get(&DataKey::Total)
            .unwrap_or(0)
    }
}
