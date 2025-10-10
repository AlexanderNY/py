from datetime import datetime
#Dp 50 (3 rep) SA Pods 50 DR 70 RB 100

#
# Настройки генерации
#
# Namespace
namespace = "ci04877421-uamc-hl-tests"  # Имя NS куда заносим конфигурации

# сколько нужно нагенерировать конфигураций
common_count = 1  # Это общее количество конфигураций
count_iter = 0  # Сброс счетчика
pv_usage = 0  # Сколько использовать PV, если ноль, то не генерируем блок

# Deployments
generate_dp = True
count_dp = 50  # common_count # Это общее количество конфигураций, подбираем, чтобы стартовали Podы
name_dp = "deployment-test-np"
replicas_dp = 3  # Подбираем, чтобы стартовали Podы
app_dp = "app-test-np"  # Label приложения
container_name_dp = "container-test-np"
container_image_dp = """>-
            registry-ci.delta.sbrf.ru/ci03745765/ci03745765/polm/proxyv2@sha256:84cf91b9c09ac0f0c94776f252f72c286cc93e1af7d6d6c7a376b779d8480a0f"""  # "nginx:stable" # Image нужно выбрать из доступных в репозитории, лучше легкий nginx
container_port_dp = 80
configmap_name_dp = "configmap-test-np" + "-0"  # ссылки будут на первую CM
secret_name_dp = "secret-test-np" + "-0"  # ссылки будут на первый Secret
container_cpu_dp = "100m"  # Подбираем, чтобы стартовал Pod
container_memory_dp = "100Mi"  # Подбираем, чтобы стартовал Pod
pv_name_dp = "data-np"  # Имя PV
pvc_name_dp = "pvc-data-np"  # Имя PVC
service_account_name_dp = "service-account-np-0"  # имя активного сервисного аккаунта

# Standalone pods
generate_sp = True
count_sp = 50  # Это общее количество конфигураций, подбираем, чтобы стартовали Podы
name_sp = "pod-test-np"
app_sp = "app-test-np"  # Label приложения
container_name_sp = "container-test-np"
container_image_sp = """>-
            registry-ci.delta.sbrf.ru/ci03745765/ci03745765/polm/proxyv2@sha256:84cf91b9c09ac0f0c94776f252f72c286cc93e1af7d6d6c7a376b779d8480a0f"""  # Image нужно выбрать из доступных в репозитории, лучше легкий nginx
container_port_sp = 80
configmap_name_sp = configmap_name_dp  # ссылки будут на первую CM - это из DP
secret_name_sp = secret_name_dp  # ссылки будутна первый Secret - это из DP
container_cpu_sp = "50m"  # Подбираем, чтобы стартовал Pod
container_memory_sp = "50Mi"  # Подбираем, чтобы стартовал Pod

# ConfigMap
generate_cm = True
count_cm = 1  # Минимум 1, т.к.исрользуется в DP, DPC, SS и т.п.
name_cm = "configmap-test-np"  # ссылки будут на первую CM - это из DP

# ServiceAccount
generate_sa = True
count_sa = 1
name_sa = "service-account-np"
namespace_sa = namespace

# Secret
generate_sec = True
count_sec = 1  # Минимум 1, т.к.исрользуется в DP, DPC, SS и т.п.
name_sec = "secret-test-np"  # ссылки будут на первый Secret - это из DP

# Service
generate_se = True
count_se = 1
name_se = "service-test-np"
app_se = "app-test-np"  # Label приложения
port_se = 80
target_port_se = 80

# Role
generate_ro = True
count_ro = 1
name_ro = "role-test-np"
namespace_ro = namespace

# RoleBinding
generate_rb = True
count_rb = 100
name_rb = "rolebinding-test-np"
namespace_rb = namespace
subject_kind_rb = "User"
subject_name_rb = "11146555"
role_kind_rb = "Role"
role_name_rb = name_ro

# Gateway
generate_gw = True
count_gw = 1
name_gw = "gateway-test-np"
label_istio_gw = "ingressgateway"

# DestinationRule
generate_dr = True
count_dr = 70
name_dr = "destinationrule-test-np"
name_service_dr = name_gw  # Gateway DR

# Ingress
generate_in = True
count_in = 1
name_in = "ingres-test-np"
name_service_in = name_se  # Service In
port_service_in = 80

# VirtualService
generate_vs = 1
count_vs = common_count
name_vs = "virtualservice-test-np"
name_gateway_vs = name_gw  # Gateway VS
name_service_vs = name_se  # Service VS

# ServiceEntry
generate_sen = True
count_sen = 1
name_sen = "serviceentry-test-np"

# Endpoints
generate_en = False  # Вопрос Николаю и Дмитрию: "зачем требуется генерация EP?"
count_en = 2
name_en = name_se  # Service EP

# StatefulSet
generate_ss = False
count_ss = common_count  # Это общее количество конфигураций, подбираем, чтобы стартовали Podы
name_ss = "statefulset-test-np"
service_name_ss = "service-ss-test-np"  # Service для SS
replicas_ss = 3
app_ss = "app-test-np"  # Label приложения
container_name_ss = "container-test-np"
container_image_ss = "nginx:stable"  # Image нужно выбрать из доступных в репозитории, лучше легкий nginx
container_port_ss = 80
configmap_name_ss = configmap_name_dp  # ссылки будут на первую CM - это из DP
secret_name_ss = secret_name_dp  # ссылки будутна первый Secret - это из DP
container_cpu_ss = "50m"  # Подбираем, чтобы стартовал Pod
container_memory_ss = "50Mi"  # Подбираем, чтобы стартовал Pod
pv_name_ss = pv_name_dp  # Имя PV - это из DP
pvc_name_ss = pvc_name_dp  # Имя PVC - это из DP
service_account_name_ss = "service-account-np-0"  # имя активного сервисного аккаунта

# PersistentVolume
generate_pv = False
count_pv = 2
name_pv = "data-np"
label_pv = "release: stable"
capacity_pv = "5Gi"
storageClassName = "slow"

# PersistentVolumeClaim
generate_pvc = False
count_pvc = 2
name_pvc = "pvc-data-np"
namespace_pvc = namespace
label_pvc = "release: stable"
capacity_pvc = "20Mi"
volumename_pvc = "vol"
storageClassName = "slow"


#
# Шаблоны генерации
#

def generate_pod_pattern(
    name_sp,
    namespace,
    app_sp,
    container_name_sp,
    container_image_sp,
    container_port_sp,
    configmap_name_sp,
    secret_name_sp,
    container_cpu_sp,
    container_memory_sp,
    pv_name_dp
):
    pod_pattern = f'''
apiVersion: v1
kind: Pod
metadata:
  name: {name_sp}
  namespace: {namespace}
  labels:
    app: {app_sp}
spec:
  containers:
    - name: {container_name_sp}
      image: {container_image_sp}
      ports:
        - containerPort: {container_port_sp}
      env:
        - name: APP_ENV
          valueFrom:
            configMapKeyRef:
              name: {configmap_name_sp} #ссылка на ConfigMap
              key: APP_ENV
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: {configmap_name_sp} #ссылка на ConfigMap
              key: LOG_LEVEL
        - name: USERNAME
          valueFrom:
            secretKeyRef:
              name: {secret_name_sp}
              key: username
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              name: {secret_name_sp}
              key: password
      readinessProbe:
        httpGet:
          path: /
          port: 80
        initialDelaySeconds: 5
        periodSeconds: 10
      livenessProbe:
        httpGet:
          path: /
          port: 80
        initialDelaySeconds: 15
        periodSeconds: 20
      resources:
        limits:
          cpu: "{container_cpu_sp}"
          memory: "{container_memory_sp}"
        requests:
          cpu: "{container_cpu_sp}"
          memory: "{container_memory_sp}"'''
    if pv_usage :
        pod_pattern =  pod_pattern + f'''
      volumeMounts:
        - name: {pv_name_dp}
          mountPath: /usr/share/nginx/html
        - name: kube-api-access-n8d5d
          mountPath: /var/run/secrets/kubernetes.io/serviceaccount
          readOnly: true
          recursiveReadOnly: Disabled'''
    pod_pattern =  pod_pattern + f'''      
  restartPolicy: Always
'''
    return(pod_pattern)

def generate_deployment_pattern(
    name_dp,
    namespace,
    replicas_dp,
    app_dp,
    container_name_dp,
    container_image_dp,
    container_port_dp,
    configmap_name_dp,
    secret_name_dp,
    container_cpu_dp,
    container_memory_dp,
    pv_name_dp,
    pvc_name_dp,
    service_account_name_dp
):
    deployment_pattern = f'''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name_dp}
  namespace: {namespace}
spec:
  replicas: {replicas_dp}
  selector:
    matchLabels:
      app: {app_dp}
  template:
    metadata:
      labels:
        app: {app_dp}
    spec:
      containers:
        - name: {container_name_dp}
          image: {container_image_dp}
          ports:
            - containerPort: {container_port_dp}
          env:
            - name: APP_ENV
              valueFrom:
                configMapKeyRef:
                  name: {configmap_name_dp} #ссылка на ConfigMap
                  key: APP_ENV
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: {configmap_name_dp} #ссылка на ConfigMap
                  key: LOG_LEVEL
            - name: USERNAME
              valueFrom:
                secretKeyRef:
                  name: {secret_name_dp}
                  key: username
            - name: PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {secret_name_dp}
                  key: password
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 15
            periodSeconds: 20
          resources: #сколько потребляет 1 контейнер
            limits:
              cpu: "{container_cpu_dp}"
              memory: "{container_memory_dp}"
            requests:
              cpu: "{container_cpu_dp}"
              memory: "{container_memory_dp}"'''
    if pv_usage :
        deployment_pattern = deployment_pattern +f'''
          volumeMounts:
            - name: pvc-data-np
              mountPath: /usr/share/nginx/html
      volumes:
        - name: {pv_name_dp}
          persistentVolumeClaim:
            claimName: {pvc_name_dp}
      restartPolicy: Always
      serviceAccountName: {service_account_name_dp}'''
    deployment_pattern = deployment_pattern + f'''
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
'''
    return(deployment_pattern)

def generate_configmap_pattern(name_cm, namespace):
    configmap_pattern = f'''
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name_cm}
  namespace: {namespace}
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
'''
    return(configmap_pattern)

def generate_secret_pattern(name_sec, namespace):
    secret_pattern = f'''
apiVersion: v1
kind: Secret
metadata:
  name: {name_sec}
  namespace: {namespace}
type: Opaque
data:
  username: YWRtaW4=        # base64 encoded 'admin'
  password: MWYyZDFlMmU2N2Rm  # base64 encoded '1f2d1e2e67df'
'''
    return(secret_pattern)

def generate_service_pattern(
    name_se,
    namespace,
    app_se,
    port_se,
    target_port_se
):
    service_pattern = f'''
apiVersion: v1
kind: Service
metadata:
  name: {name_se}
  namespace: {namespace}
spec:
  selector:
    app: {app_se}
  ports:
    - protocol: TCP
      port: {port_se}
      targetPort: {target_port_se}
  type: ClusterIP
'''
    return(service_pattern)

endpoints_pattern = f'''
apiVersion: v1
kind: Endpoints
metadata:
  name: {name_en}
  namespace: {namespace}  
subsets:
  - addresses:
      - ip: 10.0.0.1
      - ip: 10.0.0.2
    ports:
      - port: 80
        protocol: TCP
'''

def generate_statefulset_pattern(
    name_ss,
    namespace,
    service_name_ss,
    replicas_ss,
    app_ss,
    container_name_ss,
    container_image_ss,
    container_port_ss,
    configmap_name_ss,
    secret_name_ss,
    container_cpu_ss,
    container_memory_ss,
    pv_name_ss,
    pvc_name_ss,
    service_account_name_ss
):
    statefulset_pattern = f'''
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {name_ss}
  namespace: {namespace}
spec:
  serviceName: "{service_name_ss}"  # Headless service name
  replicas: {replicas_ss}
  selector:
    matchLabels:
      app: {app_ss}
  template:
    metadata:
      labels:
        app: {app_ss}
    spec:
      serviceAccountName: {service_account_name_ss}
      containers:
        - name: {container_name_ss}
          image: {container_image_ss}
          ports:
            - containerPort: {container_port_ss}
          env:
            - name: APP_ENV
              valueFrom:
                configMapKeyRef:
                  name: {configmap_name_ss} #ссылка на ConfigMap
                  key: APP_ENV
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: {configmap_name_ss} #ссылка на ConfigMap
                  key: LOG_LEVEL
            - name: USERNAME
              valueFrom:
                secretKeyRef:
                  name: {secret_name_ss}
                  key: username
            - name: PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {secret_name_ss}
                  key: password
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 15
            periodSeconds: 20
          resources:
            requests:
              cpu: "{container_cpu_ss}"
              memory: "{container_memory_ss}"
            limits:
              cpu: "{container_cpu_ss}"
              memory: "{container_memory_ss}"'''
    if pv_usage :
        statefulset_pattern =  statefulset_pattern + f'''
          volumeMounts:
            - name: {pv_name_ss}
              mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
    - metadata:
        name: {pvc_name_ss}
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard
        resources:
          requests:
            storage: 20M
'''
    return(statefulset_pattern)

def generate_ingress_pattern(
    name_in,
    namespace,
    name_service_in,
    port_service_in
):
    ingress_pattern = f'''
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {name_in}
  namespace: {namespace}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {name_service_in}
                port:
                  number: {port_service_in}
'''
    return(ingress_pattern)

def generate_virtualservice_pattern(
    name_vs,
    namespace,
    name_gateway_vs,
    name_service_vs
):
    virtualservice_pattern = f'''
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: {name_vs}
  namespace: {namespace}
spec:
  hosts:
    - "example.com"
  gateways:
    - {name_gateway_vs} 
  http:
    - match:
        - uri:
            prefix: "/"
      route:
        - destination:
            host: {name_service_vs}  
            port:
              number: 80
'''
    return(virtualservice_pattern)

def generate_destinationrule_pattern(
    name_dr,
    namespace,
    name_service_dr
):
    destinationrule_pattern = f'''
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: {name_dr}
  namespace: {namespace}
spec:
  host: {name_service_dr}
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 100
        maxRequestsPerConnection: 10
  subsets:
    - name: v1
      labels:
        version: v1
'''
    return(destinationrule_pattern)

def generate_gateway_pattern(
    name_gw,
    namespace,
    label_istio_gw
):
    gateway_pattern = f'''
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: {name_gw}
  namespace: {namespace}
spec:
  selector:
    istio: {label_istio_gw}
  servers:
    - port:
        number: 80
        name: http
        protocol: HTTP
      hosts:
        - "example.com"
'''
    return(gateway_pattern)

def generate_serviceentry_pattern(
    name_sen,
    namespace
):
    serviceentry_pattern = f'''
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: {name_sen}
  namespace: {namespace}
spec:
  hosts:
  - db.example.com
  addresses:
  - 192.168.1.100  
  ports:
  - number: 5432
    name: postgres
    protocol: TCP  
  location: MESH_EXTERNAL
'''
    return(serviceentry_pattern)

def generate_role_pattern(
    name_ro,
    namespace_ro
):
    role_pattern = f'''
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {name_ro}
  namespace: {namespace_ro}
rules:
  - verbs:
      - get
      - list
    apiGroups:
      - ''
    resources:
      - pods
      - services
  - verbs:
      - get
      - list
      - watch
    apiGroups:
      - apps
    resources:
      - deployments
'''
    return(role_pattern)

def generate_rolebinding_pattern(
    name_rb,
    namespace_rb,
    subject_kind_rb,
    subject_name_rb,
    role_kind_rb,
    role_name_rb
):
    rolebinding_pattern = f'''
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {name_rb}
  namespace: {namespace_rb}
subjects:
  - kind: {subject_kind_rb}
    name: "{subject_name_rb}"
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: {role_kind_rb}
  name: {role_name_rb}
  apiGroup: rbac.authorization.k8s.io
'''
    return(rolebinding_pattern)

def generate_serviceaccount_pattern(
    name_sa,
    namespace_sa
):
    serviceaccount_pattern = f'''
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {name_sa}
  namespace: {namespace_sa}
'''
    return(serviceaccount_pattern)

def generate_persistentvolume_pattern(
    name_pv,
    label_pv,
    capacity_pv,
    storageClassName
):
    persistentvolume_pattern = f'''
apiVersion: v1
kind: PersistentVolume
metadata:
  name: {name_pv}
  labels:
    {label_pv}
  finalizers:
    - kubernetes.io/pv-protection
spec:
  capacity:
    storage: {capacity_pv} 
  nfs:
    server: 172.17.0.2
    path: /tmp
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Recycle
  storageClassName: {storageClassName}
  mountOptions:
    - hard
    - nfsvers=4.1
  volumeMode: Filesystem
'''
    return(persistentvolume_pattern)

def generate_persistentvolumeclaim_pattern(
    name_pvc,
    namespace_pvc,
    label_pvc,
    capacity_pvc,
    volumename_pvc,
    storageClassName
):
    persistentvolumeclaim_pattern = f'''
apiVersion: v1
kind: PersistentVolume
metadata:
  name: {name_pv}
  labels:
    {label_pv}
  finalizers:
    - kubernetes.io/pv-protection
spec:
  capacity:
    storage: {capacity_pv} 
  nfs:
    server: 172.17.0.2
    path: /tmp
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Recycle
  storageClassName: {storageClassName}
  mountOptions:
    - hard
    - nfsvers=4.1
  volumeMode: Filesystem
'''
    return(persistentvolumeclaim_pattern)



#
# сама генерация файлов
#

filename_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if generate_dp:
    count_iter = 0
    tmp_file = open("deployments" + filename_datetime + ".yaml", "w+")
    while count_iter < count_dp:
        tmp_name = name_dp + "-" + str(count_iter)
        result = generate_deployment_pattern(tmp_name, namespace, replicas_dp, app_dp, container_name_dp,
                                             container_image_dp, container_port_dp, configmap_name_dp, secret_name_dp,
                                             container_cpu_dp, container_memory_dp, pv_name_dp, pvc_name_dp,
                                             service_account_name_dp)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_dp:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_sp:
    count_iter = 0
    tmp_file = open("standalone_pods" + filename_datetime + ".yaml", "w+")
    while count_iter < count_sp:
        tmp_name = name_sp + "-" + str(count_iter)
        result = generate_pod_pattern(tmp_name, namespace, app_sp, container_name_sp, container_image_sp,
                                      container_port_sp, configmap_name_sp, secret_name_sp, container_cpu_sp,
                                      container_memory_sp, pv_name_dp)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_sp:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_ss:
    count_iter = 0
    tmp_file = open("statefulset" + filename_datetime + ".yaml", "w+")
    while count_iter < count_ss:
        tmp_name = name_ss + "-" + str(count_iter)
        result = generate_statefulset_pattern(tmp_name, namespace, service_name_ss, replicas_ss, app_ss,
                                              container_name_ss, container_image_ss, container_port_ss,
                                              configmap_name_ss, secret_name_ss, container_cpu_ss, container_memory_ss,
                                              pv_name_ss, pvc_name_ss, service_account_name_ss)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_ss:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_cm:
    count_iter = 0
    tmp_file = open("configmap" + filename_datetime + ".yaml", "w+")
    while count_iter < count_cm:
        tmp_name = name_cm + "-" + str(count_iter)
        result = generate_configmap_pattern(tmp_name, namespace)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_cm:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_sec:
    count_iter = 0
    tmp_file = open("secret" + filename_datetime + ".yaml", "w+")
    while count_iter < count_sec:
        tmp_name = name_sec + "-" + str(count_iter)
        result = generate_secret_pattern(tmp_name, namespace)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_sec:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_se:
    count_iter = 0
    tmp_file = open("service" + filename_datetime + ".yaml", "w+")
    while count_iter < count_se:
        tmp_name = name_se + "-" + str(count_iter)
        result = generate_service_pattern(tmp_name, namespace, app_se, port_se, target_port_se)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_se:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_en:
    # todo how to generate
    count_iter = 0

if generate_in:
    count_iter = 0
    tmp_file = open("ingress" + filename_datetime + ".yaml", "w+")
    while count_iter < count_in:
        tmp_name = name_in + "-" + str(count_iter)
        result = generate_ingress_pattern(tmp_name, namespace, name_service_in, port_service_in)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_in:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_vs:
    count_iter = 0
    tmp_file = open("virtualservice" + filename_datetime + ".yaml", "w+")
    while count_iter < count_vs:
        tmp_name = name_vs + "-" + str(count_iter)
        result = generate_virtualservice_pattern(tmp_name, namespace, name_gateway_vs, name_service_vs)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_vs:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_dr:
    count_iter = 0
    tmp_file = open("destinationrule" + filename_datetime + ".yaml", "w+")
    while count_iter < count_dr:
        tmp_name = name_dr + "-" + str(count_iter)
        result = generate_destinationrule_pattern(tmp_name, namespace, name_service_dr)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_dr:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_gw:
    count_iter = 0
    tmp_file = open("gateway" + filename_datetime + ".yaml", "w+")
    while count_iter < count_gw:
        tmp_name = name_gw + "-" + str(count_iter)
        result = generate_gateway_pattern(tmp_name, namespace, label_istio_gw)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_gw:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_sen:
    count_iter = 0
    tmp_file = open("serviceentry" + filename_datetime + ".yaml", "w+")
    while count_iter < count_sen:
        tmp_name = name_sen + "-" + str(count_iter)
        result = generate_serviceentry_pattern(tmp_name, namespace)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_sen:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_ro:
    count_iter = 0
    tmp_file = open("role" + filename_datetime + ".yaml", "w+")
    while count_iter < count_ro:
        tmp_name = name_ro + "-" + str(count_iter)
        result = generate_role_pattern(tmp_name, namespace_ro)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_ro:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_rb:
    count_iter = 0
    tmp_file = open("rolebinding" + filename_datetime + ".yaml", "w+")
    while count_iter < count_rb:
        tmp_name = name_rb + "-" + str(count_iter)
        result = generate_rolebinding_pattern(tmp_name, namespace_rb, subject_kind_rb, subject_name_rb, role_kind_rb,
                                              role_name_rb)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_rb:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_sa:
    count_iter = 0
    tmp_file = open("serviceaccount" + filename_datetime + ".yaml", "w+")
    while count_iter < count_sa:
        tmp_name = name_sa + "-" + str(count_iter)
        result = generate_serviceaccount_pattern(tmp_name, namespace_sa)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_sa:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_pv:
    count_iter = 0
    tmp_file = open("persistentvolume" + filename_datetime + ".yaml", "w+")
    while count_iter < count_pv:
        tmp_name = name_pv + "-" + str(count_iter)
        result = generate_persistentvolume_pattern(tmp_name, label_pv, capacity_pv, storageClassName)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_pv:
            tmp_file.write("\n---")
    tmp_file.close()

if generate_pvc:
    count_iter = 0
    tmp_file = open("persistentvolumeclaim" + filename_datetime + ".yaml", "w+")
    while count_iter < count_pvc:
        tmp_name = name_pvc + "-" + str(count_iter)
        result = generate_persistentvolumeclaim_pattern(tmp_name, namespace_pvc, label_pvc, capacity_pvc,
                                                        volumename_pvc, storageClassName)
        tmp_file.write(result)
        count_iter += 1
        if count_iter < count_pvc:
            tmp_file.write("\n---")
    tmp_file.close()


