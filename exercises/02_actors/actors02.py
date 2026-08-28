"""
Exercise: exercises/02_actors/actors02.py
Topic: Actor Method Calls & State Mutation

Context & Why:
In a distributed environment, managing concurrent state safely usually requires complex locking
primitives (mutexes, semaphores). Ray Actors simplify this by executing incoming method calls
sequentially in the exact FIFO order they arrive in the actor's message queue.

Because only one method executes at a time within an actor process, state mutations like
`self.balance += amount` are inherently thread-safe and free from data races without manual locks.

Instructions:
1. Implement `BankAccount` actor with `deposit`, `withdraw`, `get_balance`, and `get_history` methods.
2. Perform deposits and withdrawals, and assert accurate final balance and transaction logs.
"""

import ray


# TODO: Decorate BankAccount with @ray.remote and implement methods
class BankAccount:
    def __init__(self, owner: str, initial_balance: float = 0.0) -> None:
        self.owner = owner
        self.balance = initial_balance
        self.history: list[str] = []

    def deposit(self, amount: float) -> float:
        # TODO: Add amount to balance, log to history, return balance
        pass

    def withdraw(self, amount: float) -> bool:
        # TODO: If sufficient balance, deduct and return True; else return False
        pass

    def get_balance(self) -> float:
        # TODO: Return current balance
        pass

    def get_history(self) -> list[str]:
        # TODO: Return history
        pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Create account for "Alice" with 100.0 initial balance
    # account = BankAccount.remote("Alice", 100.0)
    # account.deposit.remote(50.0)
    # account.withdraw.remote(30.0)
    # account.withdraw.remote(200.0)  # Should fail (insufficient funds)
    # balance = ray.get(account.get_balance.remote())
    # history = ray.get(account.get_history.remote())
    balance, history = None, None

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
