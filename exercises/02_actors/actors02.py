"""Chapter 2: Distributed State & Actors - Exercise 2: Actor Method Calls & State Mutation.

In a distributed environment, managing concurrent state safely usually requires
complex locking primitives (mutexes, semaphores). Ray Actors simplify this:

By default, an Actor executes its method calls SEQUENTIALLY in the exact FIFO order
they arrive in its mailbox.

Key Guarantees:
1. No Race Conditions on Instance State: Because only one method executes at a time
   on the actor process, `self.balance += amount` is atomic with respect to other method calls.
2. FIFO Execution: Method calls dispatched from a single worker/driver are executed in order.

Your Task:
- Implement a `BankAccount` actor:
  - `deposit(amount: float) -> float`: increases balance, appends `"deposit: <amount>"` to history, returns new balance.
  - `withdraw(amount: float) -> bool`: if balance >= amount, decreases balance, appends `"withdraw: <amount>"` to history, returns True; otherwise returns False.
  - `get_balance() -> float`: returns current balance.
  - `get_history() -> list[str]`: returns transaction history list.
- Perform a series of transactions and verify balance and history.
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
