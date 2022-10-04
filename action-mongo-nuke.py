#!/usr/bin/python3
# usage: python action-mongo-nuke.py
# export MONGODB_ATLAS_PRIVATE_KEY, MONGODB_ATLAS_PUBLIC_KEY as env variable
#########################################################################################################
# coding=utf-8
import os
import requests
import json
from requests.auth import HTTPDigestAuth
from retry import retry


def getallprojects(public, private, url):
    project_url = url + "/groups"
    response = requests.request("GET", project_url, auth=HTTPDigestAuth(public, private))
    projectlist = json.loads(response.content)
    idlist = []
    for p in projectlist['results']:
        idlist.append(p['id'])
    return idlist


def getclustername(public, private, url, id):
    cluster_url = url + "/groups/" + id + "/clusters"
    response = requests.request("GET", cluster_url, auth=HTTPDigestAuth(public, private))
    clusterlist = json.loads(response.content)
    for c in clusterlist['results']:
        clustername = c['name']
        return clustername


def deletecluster(public, private, url, id, clustername):
    cluster_delete_url = url + "/groups/" + id + "/clusters/" + clustername
    response = requests.request("DELETE", cluster_delete_url, auth=HTTPDigestAuth(public, private))
    print(response.text)


def deleteproject(public, private, url, id):
    project_delete_url = url + "/groups/" + id
    response = requests.request("DELETE", project_delete_url, auth=HTTPDigestAuth(public, private))
    print(response.text)


@retry(delay=60, tries=5)
def getclustercount(public, private, url):
    status = None
    try:
        cluster_url = url + "/clusters"
        response = requests.request("GET", cluster_url, auth=HTTPDigestAuth(public, private))
        clusterlist = json.loads(response.content)
        clustercount = clusterlist['totalCount']
        print(clustercount)
        if clustercount != 0:
            raise

    except Exception as error:
        print(error)
        raise


def main():
    base_url = "https://cloud.mongodb.com/api/atlas/v1.0"
    publickey = os.environ["MONGODB_ATLAS_PUBLIC_KEY"]
    privatekey = os.environ["MONGODB_ATLAS_PRIVATE_KEY"]

    # get all project ids in org
    idlist = getallprojects(publickey, privatekey, base_url)

    # for each project id, get clustername and delete
    for id in idlist:
        clustername = getclustername(publickey, privatekey, base_url, id)
        print(clustername)
        deletecluster(publickey, privatekey, base_url, id, clustername)

    # check current cluster count and add retry if not zero
    getclustercount(publickey, privatekey, base_url)

    # delete all projects
    for projectid in idlist:
        deleteproject(publickey, privatekey, base_url, projectid)


main()
