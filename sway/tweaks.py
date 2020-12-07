#!/usr/bin/env python3

import asyncio
from i3ipc.aio import Connection
from tendo import singleton

import wsr


async def main():
    connection = await Connection().connect()
    configuration = wsr.Configuration()
    await wsr.setup_window_renaming(connection, configuration)
    await connection.main()

me = singleton.SingleInstance()  # allow only one instance to run
asyncio.run(main())
