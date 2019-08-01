+ 30 rpm case 3 x 50 = 250 instances
    
OSM 

- ERROR Waiting ns ready at RO. RO_id=7a1cc0ba-4a77-44f0-b2a9-33b17e1f1cc4: {u'message': u'Build of instance 3f22e7ae-5346-4a0d-bb1e-ca8c78be7560 aborted: Networking client is experiencing an unauthorized exception.', u'code': 500, u'details': u' File "/opt/stack/nova/nova/compute/manager.py", line 1795, in _do_build_and_run_instance\n filter_properties)\n File "/opt/stack/nova/nova/compute/manager.py", line 1978, in _build_and_run_instance\n phase=fields.NotificationPhase.ERROR, exception=e)\n File "/usr/local/lib/python2.7/dist-packages/oslo_utils/excutils.py", line 2 ... al/lib/python2.7/dist-packages/oslo_utils/excutils.py", line 196, in force_reraise\n six.reraise(self.type_, self.value, self.tb)\n File "/opt/stack/nova/nova/compute/manager.py", line 1950, in _build_and_run_instance\n instance=instance)\n File "/usr/lib/python2.7/contextlib.py", line 35, in __exit__\n self.gen.throw(type, value, traceback)\n File "/opt/stack/nova/nova/compute/manager.py", line 2168, in _build_resources\n reason=six.text_type(exc))\n', u'created': u'2019-07-30T19:00:20Z'}

- ERROR Creating nsd=cirros_case3-ns at RO: Traceback (most recent call last): File "/usr/lib/python3.5/asyncio/selector_events.py", line 662, in _read_ready data = self._sock.recv(self.max_size) ConnectionResetError: [Errno 104] Connection reset by peer The above exception was the direct cause of the following exception: Traceback (most recent call last): File "/usr/lib/python3/dist-packages/aiohttp/client.py", line 178, in _request yield from resp.start(conn, read_until_eof) File "/usr/lib/python3/dist-packages/aiohttp/client_reqrep.py", line 597, in start message = yield from httpstream.read() File "/usr/lib/python3/dist-packages/aiohttp/streams.py", line 578, in read result = yield from super().read() File "/usr/lib/python3/dist-packages/aiohttp/streams.py", line 433, in read yield from self._waiter File "/usr/lib/python3.5/asyncio/futures.py", line 361, in __iter__ yield self # This tells Task to wait for completion. File "/usr/lib/python3.5/asyncio/tasks.py", line 296, in _wakeup future.result() File "/usr/lib/python3.5/asyncio/futures.py", line 274, in result raise self._exception aiohttp.errors.ServerDisconnectedError The above exception was the direct cause of the following exception: Traceback (most recent call last): File "/usr/lib/python3/dist-packages/osm_lcm/ns.py", line 734, in instantiate desc = await RO.create("nsd", descriptor=nsd_RO) File "/usr/lib/python3/dist-packages/osm_lcm/ROclient.py", line 803, in create all_tenants=all_tenants) File "/usr/lib/python3/dist-packages/osm_lcm/ROclient.py", line 518, in _create_item async with session.post(url, headers=self.headers_req, data=payload_req) as response: File "/usr/lib/python3/dist-packages/aiohttp/client.py", line 504, in __aenter__ self._resp = yield from self._coro File "/usr/lib/python3/dist-packages/aiohttp/client.py", line 185, in _request raise aiohttp.ClientResponseError() from exc aiohttp.errors.ClientResponseError 

OpenStack

- Build of instance e6fc29df-0ecd-4dc5-91fe-ee79929244cf aborted: Networking client is experiencing an unauthorized exception.

- File "/opt/stack/nova/nova/compute/manager.py", line 1795, in _do_build_and_run_instance filter_properties) File "/opt/stack/nova/nova/compute/manager.py", line 1978, in _build_and_run_instance phase=fields.NotificationPhase.ERROR, exception=e) File "/usr/local/lib/python2.7/dist-packages/oslo_utils/excutils.py", line 220, in __exit__ self.force_reraise() File "/usr/local/lib/python2.7/dist-packages/oslo_utils/excutils.py", line 196, in force_reraise six.reraise(self.type_, self.value, self.tb) File "/opt/stack/nova/nova/compute/manager.py", line 1950, in _build_and_run_instance instance=instance) File "/usr/lib/python2.7/contextlib.py", line 35, in __exit__ self.gen.throw(type, value, traceback) File "/opt/stack/nova/nova/compute/manager.py", line 2168, in _build_resources reason=six.text_type(exc))


# 10 rpm gives 241 success with all errors aassociated with below

# 30 rpm by increasing the token expiration
    - 230 - connection reset error at osm

# 15 rpm by increasing the token expiration
    - 
    - Build of instance 7c688ef4-5c01-4486-ad07-00a96f7198b5 aborted: Networking client is experiencing an unauthorized exception.