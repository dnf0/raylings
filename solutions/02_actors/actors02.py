"""Chapter 2: Distributed State & Actors - Solution 2: Actor Method Calls & State Mutation.

Reference Solution for actors02.
"""

import ray


@ray.remote
class BankAccount:
    def __init__(self, owner: str, initial_balance: float = 0.0) -> None:
        self.owner = owner
        self.balance = initial_balance
        self.history: list[str] = []

    def deposit(self, amount: float) -> float:
        self.balance += amount
        self.history.append(f"deposit: {amount}")
        return self.balance

    def withdraw(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            self.history.append(f"withdraw: {amount}")
            return True
        return False

    def get_balance(self) -> float:
        return self.balance

    def get_history(self) -> list[str]:
        return self.history


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    account = BankAccount.remote("Alice", 100.0)
    account.deposit.remote(50.0)
    account.withdraw.remote(30.0)
    account.withdraw.remote(200.0)  # Should fail (insufficient funds)
    balance = ray.get(account.get_balance.remote())
    history = ray.get(account.get_history.remote())

    assert balance == 120.0, f"Expected balance 120.0, got {balance}"
    assert history == [
        "deposit: 50.0",
        "withdraw: 30.0",
    ], f"Unexpected history: {history}"
    print(
        f"✓ actors02 verified: BankAccount actor state mutations processed sequentially (balance={balance})!"
    )


if __name__ == "__main__":
    verify()
