# Copyright 2016 Rackspace Hosting Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron_lib import exceptions as n_exc
from oslo_config import cfg
from oslo_log import log as logging

from quark.db import api as db_api
from quark import exceptions as q_exc
from quark import plugin_views as v

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def add_job_to_context(context, job_id):
    """Adds job to neutron context for use later."""
    db_job = db_api.async_transaction_find(
        context, id=job_id, scope=db_api.ONE)
    if not db_job:
        return
    context.async_job = {"job": v._make_job_dict(db_job)}


def get_jobs(context, **filters):
    LOG.info("get_jobs for tenant %s" % context.tenant_id)
    if not filters:
        filters = {}
    jobs = db_api.async_transaction_find(context, scope=db_api.ALL, **filters)
    return [v._make_job_dict(ip) for ip in jobs]


def get_job(context, id):
    LOG.info("get_job %s for tenant %s" % (id, context.tenant_id))
    filters = {}
    job = db_api.async_transaction_find(context, id=id, scope=db_api.ONE,
                                        **filters)
    if not job:
        raise q_exc.JobNotFound(job_id=id)
    return v._make_job_dict(job)


def create_job(context, body):
    """Creates a job with support for subjobs.

    If parent_id is not in the body:
    * the job is considered a parent job
    * it will have a NULL transaction id
    * its transaction id == its id
    * all subjobs will use its transaction id as theirs

    Else:
    * the job is a sub job
    * the parent id is the id passed in
    * the transaction id is the root of the job tree
    """
    LOG.info("create_job for tenant %s" % context.tenant_id)

    if not context.is_admin:
        raise n_exc.NotAuthorized()
    job = body.get('job')
    if 'parent_id' in job:
        parent_id = job['parent_id']
        if not parent_id:
            raise q_exc.JobNotFound(job_id=parent_id)
        parent_job = db_api.async_transaction_find(
            context, id=parent_id, scope=db_api.ONE)
        if not parent_job:
            raise q_exc.JobNotFound(job_id=parent_id)
        tid = parent_id
        if parent_job.get('transaction_id'):
            tid = parent_job.get('transaction_id')
        job['transaction_id'] = tid

    if not job:
        raise n_exc.BadRequest(resource="job", msg="Invalid request body.")
    with context.session.begin(subtransactions=True):
        new_job = db_api.async_transaction_create(context, **job)
    return v._make_job_dict(new_job)


def update_job(context, id, body):
    LOG.info("update_job %s for tenant %s" % (id, context.tenant_id))

    if not context.is_admin:
        raise n_exc.NotAuthorized()
    job_update = body.get('job')
    if not job_update:
        raise n_exc.BadRequest(resource="job", msg="Invalid request body.")
    job = db_api.async_transaction_find(context, id=id, scope=db_api.ONE)
    if not job:
        raise q_exc.JobNotFound(job_id=id)
    job_mod = db_api.async_transaction_update(context, job, **job_update)
    return v._make_job_dict(job_mod)


def delete_job(context, id, **filters):
    """Delete an ip address.

    : param context: neutron api request context
    : param id: UUID representing the ip address to delete.
    """
    LOG.info("delete_ip_address %s for tenant %s" % (id, context.tenant_id))

    if not context.is_admin:
        raise n_exc.NotAuthorized()
    with context.session.begin():
        job = db_api.async_transaction_find(context, id=id, scope=db_api.ONE,
                                            **filters)
        if not job:
            raise q_exc.JobNotFound(job_id=id)
        db_api.async_transaction_delete(context, job)
