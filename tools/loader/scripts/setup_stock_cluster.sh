#!/usr/bin/env bash
SERVER=$1

cd
source ~/Projects/Research/loader/scripts/cluster_config

server_exec() { 
    ssh -oStrictHostKeyChecking=no -p 22 "$SERVER" $1; 
}

# Spin up vHive under container mode.
server_exec 'sudo DEBIAN_FRONTEND=noninteractive apt-get autoremove' 
server_exec "git clone --branch=$VHIVE_BRANCH https://github.com/ease-lab/vhive"
server_exec 'cd vhive; ./scripts/cloudlab/setup_node.sh stock-only'
server_exec 'tmux new -d -s containerd'
server_exec 'tmux new -d -s cluster'
server_exec 'tmux send-keys -t containerd "sudo containerd" ENTER'
sleep 3s
server_exec 'cd vhive; ./scripts/cluster/create_one_node_cluster.sh stock-only'
# sleep 4m
server_exec 'tmux send-keys -t cluster "watch -n 0.5 kubectl get pods -A" ENTER'

# Update golang.
server_exec 'wget https://dl.google.com/go/go1.17.linux-amd64.tar.gz'
server_exec 'sudo rm -rf /usr/local/go && sudo tar -C /usr/local/ -xzf go1.17.linux-amd64.tar.gz'
server_exec 'rm go1.17*'
server_exec 'echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.profile'
server_exec 'source ~/.profile'

# Setup github authentication.
ACCESS_TOKEH="$(cat ~/Projects/Research/access_token.github)"

server_exec 'echo -en "\n\n" | ssh-keygen -t rsa'
server_exec 'ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts'
# server_exec 'RSA=$(cat ~/.ssh/id_rsa.pub)'

server_exec 'curl -H "Authorization: token '"$ACCESS_TOKEH"'" --data "{\"title\":\"'"key:\$(hostname)"'\",\"key\":\"'"\$(cat ~/.ssh/id_rsa.pub)"'\"}" https://api.github.com/user/keys'
# server_exec 'sleep 5'

# Get loader.
server_exec "git clone --branch=$LOADER_BRANCH git@github.com:eth-easl/loader.git"

cd -