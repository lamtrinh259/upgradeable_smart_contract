from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)


def main():
    account = get_account()
    print(f"Deploying to  {network.show_active()}")
    # pubish_source will show the contract on ethscan
    box = Box.deploy({"from": account}, publish_source=True)
    # This should print 0
    print(box.retrieve())
    # Proxy admin
    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)
    # Encode the initializer function
    initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()

    # The proxy is the one whose code can be changed
    proxy = TransparentUpgradeableProxy.deploy(
        # gas_limit is optional
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=True,
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    box.store(1)
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    # Upgrade the contract
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    # This should return 2 since the proxy box started with 1
    print(proxy_box.retrieve())
