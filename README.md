# Quick and Dirty Ansible Collections Demo

This originally started with someone expressing frustration around using jinja to strip out terminating ':'
from JSON output. 

https://www.reddit.com/r/ansible/comments/l5j6z5/removing_from_a_dictionary_key/

I made the suggestion, that when things get "stupid complicated" in Jinja, it is much simpler to do 
custom work in Python - even if you don't know Python that much - this is actually a good introduction.

So, following : https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

I set about creating my first pass - all was well with the world except - I could not release it as it was in the core modules. 

I posted my code, with a note, to explore collections - which was a much better way to distribute evrything (as opposed to previous ways)

# The Next step

So now armed with a little code... lets make a collection - Wow .. that was easy.

Reading up on : https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html


Or more precicely : https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html#creating-collections

I did the following : 

    ansible-galaxy collection init alainchiasson.inhouse

This created a really basic structure ( as documented ). From my previous experince ( in the core ansible ), I created My module directory:

    mkdir alainchaisson/inhouse/plugins/modules
    cp lscpu_facts.py alainchaisson/inhouse/plugins/modules/

Now we can build and locally install our module.

    ansible-galaxy collection build alainchiasson/inhouse 

This cretes a tar file ( alainchiasson-inhouse-1.0.0.tar ). See the galaxy.yml file for more inforamtion. We then install from the file.

    ansible-galaxy collection install alainchiasson-inhouse-1.0.0.tar

And we can then run manual tests (I need automated ones and error catching !!)

    ansible localhost -m alainchiasson.inhouse.lscpu
    ansible-playbook playbook.yml

This is sufficient. but to keep things a little modular and clean (minimal). We can move the get_lscpu to a utility module.

    mkdir alainchaisson/inhouse/plugins/module_util
    touch alainchaisson/inhouse/plugins/module_util/helpers.py

In that file, we add our lscpu function ( from the previous module ), and wrap it with the classic Python main vs module. This allows us to run : 

    python3 helpers

Without needing all the ansible bagage ( nice for testing - see python ). Now we need to "integrate" with the new utility module. But this helps segregate where our code is.

    from ansible_collections.alainchiasson.inhouse.plugins.module_utils.helpers import get_lscpu

And remove the old function - the remainder of the code can stay the same. Now build and deploy - in this case, since we are tesitng, we need to force the build and install.

    ansible-galaxy collection build --force alainchiasson/inhouse 
    ansible-galaxy collection install --force alainchiasson-inhouse-1.0.0.tar

And validate again.

    ansible localhost -m alainchiasson.inhouse.lscpu
    ansible-playbook playbook.yml

Thats it ... well there is more ... the goal was to get around unitelligible jinja.

# Getting it running from the repo via docker 

I like to spin up docker environments when doing this. So I'm adding these notes. from the repo root :

    docker run -it --rm -v $(pwd):/workspace centos
    yum install -y epel-release
    yum install -y python3 ansible

( yeah - I could just create a dcokerimage and Dockerfile for that )

As all the code is there, the above steps are not needed ( the init ). As well, the original collections init created a directory structure 'alainchiasson/inhouse' 
which is ok if I am building mutliple collections in the same namespace, but for the repo I removed one layer. The namespace is still defined in the galaxy.yml file,
So the install path will be the same, as will the library path ( for the includes). The following commands are still needed to build and install, and they change a 
little from the above commands to reflect the change. You will notice that the tar mname is still the same.

    ansible-galaxy collection build --force inhouse 
    ansible-galaxy collection install --force alainchiasson-inhouse-1.0.0.tar

And from there you may run the two validation tests we have : 

    ansible localhost -m alainchiasson.inhouse.lscpu
    ansible-playbook playbook.yml

# Building a runnable docker image.

I have also added a dockerfile that will package the above steps to build a dockerimage that runs to demonstrate the playbook.

    docker build -t ansible-lscpu-example .

This will build a fedora based image with python and ansible. It will also copy the code, build a tar, and install the lscpu module from the alainchiasson.inhouse collection. The image is self contained, to test this, we launch the image interactively : 

    docker run -it --rm ansible-lscpu-example

It drops you in a shell. You can then run the playbook:

    ansible-playbook -i localhost, -c local playbook.yml

And the expected output is the results of the lscpu as a dict. A specific key ( Vendor ID ), followed by a list of keys - using the standard jinja filter.

Or you can do it all one shot:

    docker run --rm ansible-lscpu-example ansible-playbook -i localhost, -c local  playbook.yml

On my system, the debug task:

```
  - name: get lscpu facts
    alainchiasson.inhouse.lscpu_facts:
  - name: Dump
    debug:
      msg: "{{ hostvars[inventory_hostname].lscpu }}"
  - name: Vendor ID
    debug:
      msg: "{{ hostvars[inventory_hostname].lscpu['Vendor ID'] }}"

```

shows :

```
...

TASK [Dump] ********************************************************************
ok: [localhost] => {
    "msg": {
        "Architecture": "aarch64",
        "BogoMIPS": "48.00",
        "Byte Order": "Little Endian",
        "CPU op-mode(s)": "64-bit",
...
    }
}

TASK [Dump Vendor ID] **********************************************************
ok: [localhost] => {
    "msg": "Apple"
}

TASK [Dump Keys] ***************************************************************
ok: [localhost] => {
    "msg": [
        "Architecture",
        "CPU op-mode(s)",
        "Byte Order",
        "CPU(s)",
        "On-line CPU(s) list",
        "Vendor ID",
        "Model name",
        "Model",
        "Thread(s) per core",
        "Core(s) per cluster",
        "Socket(s)",
        "Cluster(s)",
...
        "Vulnerability Spectre v2",
        "Vulnerability Srbds",
        "Vulnerability Tsx async abort"
    ]
}

```


