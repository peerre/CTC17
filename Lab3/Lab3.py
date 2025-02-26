import time, sys, math, random

# Legenda do código usado para profissões
occupations = {
    0:  "other",
    1:  "academic/educator",
    2:  "artist",
    3:  "clerical/admin",
    4:  "college/grad student",
    5:  "customer service",
    6:  "doctor/health care",
    7:  "executive/managerial",
    8:  "farmer",
    9:  "homemaker",
    10:  "K-12 student",
    11:  "lawyer",
    12:  "programmer",
    13:  "retired",
    14:  "sales/marketing",
    15:  "scientist",
    16:  "self-employed",
    17:  "technician/engineer",
    18:  "tradesman/craftsman",
    19:  "unemployed",
    20:  "writer"
}


def printMatrix(mat, f):
    for i in range(len(mat) + 1):
        f.write("|%6d" % i)
    f.write("\n")
    for i in range(len(mat)):
        f.write("|%6d" % (i+1))
        for j in range(len(mat[i])):
            f.write("|%6d" % mat[i][j])
        f.write("|\n")
    f.write("\n")


class Variable:
    # Classe Variable representa um dos atributos possíveis de uma rating, com nome e domínio
    def __init__(self, name, domain):
        self.name = name
        self.domain = domain


class Movie:
    # Classe Movie representa um filme, com id, nome, ano e lista de gêneros e score
    def __init__(self, id, name, year, genres, score):
        self.id = id
        self.name = name
        self.year = year
        self.genres = genres
        self.score = score


class Person:
    # Classe Person representa um usuário, com id, gênero, idade e profissão
    def __init__(self, id, gender, age, profession):
        self.id = id
        self.gender = gender
        self.age = age
        self.profession = profession


class Rating:
    # Classe Rating representa uma avaliação, com sua pontuação, seu filme/id do filme ou usuário/id do usuário
    def __init__(self, userid, movieid, rating, user=None, movie=None):
        self.userid = userid
        self.user = user
        self.movieid = movieid
        self.movie = movie
        self.score = rating

    def getValue(self, var):
        # função para retornar os valores relativos a uma Variable recebida como parâmetro
        if var.name == "name":
            if self.movie is None:
                self.movie = findId(movies, self.movieid, 0, len(movies) - 1)
            return self.movie.name
        if var.name == "genre":
            if self.movie is None:
                self.movie = findId(movies, self.movieid, 0, len(movies) - 1)
            return self.movie.genres
        if var.name == "age":
            if self.user is None:
                self.user = findId(people, self.userid, 0, len(people) - 1)
            return self.user.age
        if var.name == "occupation":
            if self.user is None:
                self.user = findId(people, self.userid, 0, len(people) - 1)
            return self.user.profession
        if var.name == "gender":
            if self.user is None:
                self.user = findId(people, self.userid, 0, len(people) - 1)
            return self.user.gender


def findId(vector, id, beg, end):
    # Busca binária para encontrar um usuário ou um filme com seu ID
    if beg > end:
        return vector[0]
    else:
        if vector[beg].id == id:
            return vector[beg]

        med = int((beg + end) / 2)
        if vector[med].id == id:
            return vector[med]
        elif vector[med].id > id:
            return findId(vector, id, beg, med - 1)
        elif vector[med].id < id:
            return findId(vector, id, med + 1, end)


def ratingCount(ratings):
    # Função que retorna distribuição das pontuações da lista de ratings que é parâmetro
    counters = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0
    }
    for r in ratings:
        counters[r.score] += 1
    return counters


def majorityRating(ratings):
    # Função que calcula a pontuação majoritária e a sua probabilidade
    counters = ratingCount(ratings)
    cmax = 0
    rmax = 0
    for c, v in counters.items():
        rmax = c if v > cmax else rmax
        cmax = v if v > cmax else cmax
    return rmax, cmax/len(ratings)


def separateVar(ratings, var):
    # Função que separa uma lista de ratings em várias de acordo com uma variável
    attrDict = {}
    for val in var.domain:
        attrDict[val] = []
    for rat in ratings:
        val = rat.getValue(var)
        if type(val) is list:
            for v in val:
                attrDict[v].append(rat)
        else:
            attrDict[val].append(rat)
    return attrDict


def calcEntropy(ratings):
    # Função que calcula a entropia de uma lista de ratings
    counters = ratingCount(ratings)
    total = 0
    entropy = 0
    for val in counters:
        # print("\t\t\t\tval {}: {}".format(val, counters[val]))
        total += counters[val]
    # print("\t\t\tEntropy = ",end="")
    for val in counters:
        if counters[val] > 0:
            percent = counters[val]/total
            entropy += -1*percent*(math.log(percent,2))
            # print("- {0:.3f} * log2({0:.3f}) (={1:.3f})".format(percent, entropy), end="")
    # print("")
    return entropy


def chooseBest(vars, ratings):
    # Função que escolhe qual variável divide a lista de ratings com um maior ganho de informação (diminuição de entropia)
    entropyInit = calcEntropy(ratings)
    # print("Initial entropy: {}".format(entropyInit))
    maxgain = 0
    varmaxgain = None
    for var in vars:
        # print("\tSeparating with {}".format(var.name))
        attrDict = separateVar(ratings, var)
        newEntropy = 0
        for val in var.domain:
            ent = calcEntropy(attrDict[val])
            attrsum = 0
            for attr in attrDict:
                attrsum += len(attrDict[attr])
            # print("\t\tEntropy for value {}: {}/{} * {}".format(val, len(attrDict[val]), attrsum, ent))
            newEntropy += (len(attrDict[val])/attrsum)*ent
        gain = entropyInit - newEntropy
        # print("\tNew entropy: {} --> gain: {}".format(newEntropy, gain))
        varmaxgain = var if gain > maxgain else varmaxgain
        maxgain = gain if gain > maxgain else maxgain
    # print("Variable chosen: {}, with gain of {}".format(varmaxgain.name, maxgain))
    return varmaxgain


class TreeNode:
    # Classe nó da árvore de decisão
    def __init__(self, vars, ratings, default, father, height):
        # Função init é o algoritmo (recursivo)_de formação de árvore de decisão, que recebe a lista de ratings, de
        # variáveis que ainda podem ser usadas para decisão, o valor default da pontuação, o pai do nó atual e a altura
        # do nó atual
        self.father = father
        self.height = height
        self.children = []

        # Test: are there too few ratings?
        # pruningFactor = fator de poda, definido na main
        # lenRat = tamanho da base de dados original, calculado na main
        if len(ratings) < pruningFactor*lenRat:
            self.leaf = True
            if len(ratings) == 0:
                self.dist = default
            else:
                self.dist = ratingCount(ratings)
                for rat in self.dist:
                    self.dist[rat] /= len(ratings)
                # print("Too few examples left, using default: {}".format(self.value))
                return

        # Test: are all ratings the same?
        val = None
        equal = True
        for r in ratings:
            if val is None:
                val = r.score
            elif r.score != val:
                equal = False
                break
        if equal:
            # print("All examples equal, using value: {}".format(val))
            self.leaf = True
            self.dist = {1: 0, 2:0, 3:0, 4:0, 5:0}
            self.dist[val] = 1
            return

        # Test: are there no more variables?
        if len(vars) == 0:
            self.leaf = True
            self.dist = ratingCount(ratings)
            for rat in self.dist:
                self.dist[rat] /= len(ratings)
            # print("No variables left, using majority: {}".format(self.value))
            return

        # Algorithm
        self.var = chooseBest(vars, ratings)
        self.dist = ratingCount(ratings)
        for rat in self.dist:
            self.dist[rat] /= len(ratings)

        # print("Current prediction: {} with probability {}".format(self.value, self.prob))

        self.leaf = False
        examples = separateVar(ratings, self.var)
        # print("Choosing to fan out variable {}".format(self.var.name))
        for val in self.var.domain:
            examplesi = examples[val]
            varsi = vars.copy()
            varsi.remove(self.var)
            # print("Creating child with {} = {} --> {} examples".format(self.var.name, val, len(examplesi)))
            self.children.append(TreeNode(varsi, examplesi.copy(), self.dist, self, self.height + 1))

# def printTree(root, f):
#     cont = 1
#     queue = [root]
#     curheight = root.height
#     val = None
#     count = 1
#     while len(queue) > 0:
#         node = queue[0]
#         queue.pop(0)
#         if curheight != node.height:
#             count = 1
#             f.write("\n")
#             curheight = node.height
#         if node.father is None:
#             if node.leaf:
#                 f.write("\t\t(leaf: rat:{}, p:{}\n".format(node.value, node.prob))
#
#             else:
#                 f.write("\t({}?)\n".format(node.var.name))
#                 queue.extend(node.children)
#         else:
#             branch = node.father.var.domain[node.father.children.index(node)]
#             if node.leaf:
#                 f.write("\t\t(leaf: {} = {}, rat:{} p:{:.3f})\n".format(node.father.var.name, branch, node.value, node.prob))
#             else:
#                 f.write("\t({} = {}, {}?)\n".format(node.father.var.name, branch, node.var.name))
#                 queue.extend(node.children)

def printTree(root, f, tab):
    cont = 1
    queue = [root]
    curheight = root.height
    val = None
    count = 1
    tab += "\t"

    while len(queue) > 0:
        node = queue[0]
        queue.pop(0)
        if curheight != node.height:
            count = 1
            f.write("\n")
            curheight = node.height
        if node.father is None:
            if node.leaf:
                f.write("{}(leaf: rat, p:{}\n".format(tab, node.dist))

            else:
                f.write("{}({}?)\n".format(tab,node.var.name))
                # queue.extend(node.children)
                for i in range(len(node.children)):
                    printTree(node.children[i], f, tab)
        else:
            branch = node.father.var.domain[node.father.children.index(node)]
            if node.leaf:
                f.write("{}(leaf: {} = {}, rat, p:{} )\n".format(tab,node.father.var.name, branch, node.dist))
            else:
                f.write("{}({} = {}, {}?)\n".format(tab,node.father.var.name, branch, node.var.name))
                # queue.extend(node.children)
                for i in range(len(node.children)):
                    printTree(node.children[i], f, tab)


def separateTrainingData(data, p):
    train = []
    test = []
    for d in data:
        decision = random.random()
        if decision < p:
            train.append(d)
        else:
            test.append(d)
    return train, test


def applyTree(tree, testData):
    scores = []
    for i in range(len(testData)):
        r, prob = applyTreeRecursive(tree, testData[i])
        scores.append(r)
    return scores


def applyTreeRecursive(tree, data):
    if tree.leaf == True:
        dice = random.random()
        cumulative = 0
        value = 0
        for score in tree.dist:
            cumulative += tree.dist[score]
            if dice < cumulative:
                value = score
                break
        return (value, tree.dist[value])
    else:
        queue = tree.children
        # se o atributo for genero
        if tree.var.name == "genre":
            #obtem o id do filme e apos os generos
            g = data.getValue(tree.var)
            rMax = 0
            probMax = 0
            # para cada classificacao de genre do filme, obter o score
            for k in range(len(g)):
                node = queue[tree.var.domain.index(g[k])]
                r, prob = applyTreeRecursive(node, data)
                # armazena o score que apresenta a maior probabilidade
                if prob > probMax:
                    probMax = prob
                    rMax = r
            prob = probMax
            r = rMax
        else:
            carac = data.getValue(tree.var)
            node = queue[tree.var.domain.index(carac)]
            r, prob = applyTreeRecursive(node, data)
        return (r, prob)


def applyAPriori(testData, test):
    score = []
    for i in range(len(test)):
        filme_id = test[i].movieid
        aux = findId(testData, int(filme_id), 0, len(testData)-1)
        score.append(aux.score)
    return score

def trainingAPriori(testData, ratings):
    #obter o ultimo id de filme
    n = len(testData)
    final_id = (testData[n-1].id)

    quant = [0]*(final_id + 1)
    score = [0]*(final_id + 1)

    # contabilizar score e avaliacoes por filme
    for i in range(len(ratings)):
        id = ratings[i].movieid
        quant[id] += 1
        score[id] += ratings[i].score


    for i in range(len(quant)-1):
        j = findId(testData,i+1,0, len(testData)-1)
        if quant[i+1] == 0:
            pass
        else:
            rate = score[i+1]/quant[i+1]
            j.score = round(rate)


def createConfusionMatrix(testData, results):
    confMat = [[0 for i in range(5)] for j in range(5)]
    for k in range(len(results)):
        if results[k] is not None and testData[k].score is not None:
            i = results[k] - 1
            j = testData[k].score - 1
            confMat[i][j] += 1
    return confMat

def accuracy(mat):
    errorMat = []
    for i in range(5):
        errorMat.append([])
        for j in range(5):
            errorMat[i].append(abs(i-j))
    # den = pesoMax * nAmostras
    quant = 0
    for i in range(5):
        for j in range(5):
            quant += mat[i][j]
    error = 0
    for i in range(5):
        for j in range(5):
            if i != j:
                error += mat[i][j] / quant
    return 1 - error


def weightedAccuracy(mat):
    errorMat = []
    for i in range(5):
        errorMat.append([])
        for j in range(5):
            errorMat[i].append(abs(i-j))
    # den = pesoMax * nAmostras
    den = 0
    for i in range(5):
        for j in range(5):
            den += 4*mat[i][j]
    error = 0
    for i in range(5):
        for j in range(5):
            error += mat[i][j] * errorMat[i][j] / den
    return 1 - error


def treeRecommend(tree, user):
    recs = [0, 0, 0]
    probs = [0, 0, 0]
    movRecommend = [movies[0],movies[0],movies[0]]
    for mov in movies:
        rat = Rating(user.id, mov.id, 0, user, mov)
        r, prob = applyTreeRecursive(tree, rat)
        if recs[2] < r or (recs[2] == r and probs[2] < prob):
            if recs[1] < r or (recs[1] == r and probs[1] < prob):
                if recs[0] < r or (recs[0] == r and probs[0] < prob):
                    recs[2] = recs[1]
                    probs[2] = probs[1]
                    movRecommend[2] = movRecommend[1]
                    recs[1] = recs[0]
                    probs[1] = probs[0]
                    movRecommend[1] = movRecommend[0]
                    recs[0] = r
                    probs[0] = prob
                    movRecommend[0] = mov
                else:
                    recs[2] = recs[1]
                    probs[2] = probs[1]
                    movRecommend[2] = movRecommend[1]
                    recs[1] = r
                    probs[1] = prob
                    movRecommend[1] = mov
            else:
                recs[2] = r
                probs[2] = prob
                movRecommend[2] = mov
    return movRecommend


def aPrioriRecommend():
    recs = [0, 0, 0]
    movRecommend = [movies[0],movies[0],movies[0]]
    for mov in movies:
        r = mov.score
        if recs[2] < r:
            if recs[1] < r:
                if recs[0] < r:
                    recs[2] = recs[1]
                    movRecommend[2] = movRecommend[1]
                    recs[1] = recs[0]
                    movRecommend[1] = movRecommend[0]
                    recs[0] = r
                    movRecommend[0] = mov

                else:
                    recs[2] = recs[1]
                    movRecommend[2] = movRecommend[1]
                    recs[1] = r
                    movRecommend[1] = mov
            else:
                recs[2] = r
                movRecommend[2] = mov

    return movRecommend



if __name__ == '__main__':
    ratio = 0.7
    pruningFactor = 0.1
    ##################################
    # 3.1 DATA ANALYSIS              #
    ##################################
    vars = []

    varage = Variable("age", [1, 18, 25, 35, 45, 50, 56])
    vars.append(varage)

    vargender = Variable("gender", ["M", "F"])
    vars.append(vargender)
    vargenre = Variable("genre", ["Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary",
                                   "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi",
                                   "Thriller", "War", "Western"])
    vars.append(vargenre)
    varoccup = Variable("occupation", [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
    vars.append(varoccup)

    people = []
    peoplefile = open("ml-1m/users.dat",  "r")
    movies = []
    moviesfile = open("ml-1m/movies.dat", encoding="ISO-8859-1")
    ratings = []
    ratingfile = open("ml-1m/ratings.dat","r")

    #TRECHO ALTERADO PARA QUE FUNCIONE NO MAC
    # ratingfile = open("ml-1m/rat.txt","r")
    # people = []
    # peoplefile = open("ml-1m\\users.dat",  "r")
    # movies = []
    # moviesfile = open("ml-1m\\movies.dat", "r")
    # ratings = []
    # ratingfile = open("ml-1m\\ratings.dat","r")

    ini = time.time()
    for line in peoplefile.readlines():
        user = int(line.split("::")[0])
        gender = line.split("::")[1]
        age = int(line.split("::")[2])
        occupation = int(line.split("::")[3])
        people.append(Person(user, gender, age, occupation))
    print("Read people!")
    for line in moviesfile.readlines():
        id = int(line.split("::")[0])
        name = line.split("::")[1]
        year = int(name.split("(")[-1][0:-1])
        name = name.split("(")[0][0:-1]
        genres = line.replace("\n", "").split("::")[2].split("|")
        score = 0
        movies.append(Movie(id, name, year, genres, score))
    print("Read movies!")
    for line in ratingfile.readlines():
        user = int(line.split("::")[0])
        movie = int(line.split("::")[1])
        score = int(line.split("::")[2])
        ratings.append(Rating(user, movie, score))
    print("Read ratings!")
    lenRat = len(ratings)
    readTime = time.time() - ini
    print("Reading time: %.3f s" % readTime)
    ini = time.time()
    for r in ratings:
        if r.movie is None:
            r.movie = findId(movies, r.movieid, 0, len(movies)-1)
        if r.user is None:
            r.user = findId(people, r.userid, 0, len(people)-1)
    joinTime = time.time() - ini
    print("Joining time: %.3f s" % joinTime)

    ##################################
    # 3.2 DECISION TREE CLASSIFIER   #
    ##################################

    pruningFactor = 0.001
    # dist = ratingCount(ratings)
    # for rat in dist:
    #     dist[rat] /= len(ratings)
    # print("A priori: rating {} with probability {}".format(majority, prob))
    # decisionTree = TreeNode(vars, ratings, dist, None, 0)

    debug = open("debug.txt", "w")

    ##################################
    # 3.3 RANDOM CLASSIFIER          #
    ##################################
    # print("Classificador a priori")

    # ESTE TREINO PODE SER EXCLUIDO
    # treinando classificador com todos os dados
    # trainingAPriori(movies, ratings)

    ##################################
    # 3.4 CLASSIFIER COMPARISON      #
    ##################################
    print("Separating training and test...")
    ini = time.time()
    ratTrain, ratTest = separateTrainingData(ratings, ratio)
    separTime = time.time() - ini
    print("Separation time: %.3f s" % separTime)

    # Treinamento da árvore só com os dados de treinamento
    dist = ratingCount(ratTrain)
    for rat in dist:
        dist[rat] /= len(ratTrain)
    ini = time.time()
    decisionTree = TreeNode(vars, ratTrain, dist, None, 0)
    trainTime = time.time() - ini
    print("Training time: %.3f s" % trainTime)
    tab = " "
    printTree(decisionTree, debug, tab)

    # Acurácia da árvore
    ini = time.time()
    result = applyTree(decisionTree, ratTest)
    testTime = time.time() - ini
    print("Test time: %.3f s" % testTime)
    confMatrix = createConfusionMatrix(ratTest, result)
    printMatrix(confMatrix, sys.stdout)
    acTree = accuracy(confMatrix)
    wAcTree = weightedAccuracy(confMatrix)

    # Acurácia do classificador a priori
    trainingAPriori(movies, ratTrain)
    # result e um vetorr com score de todos contidos no ratTest
    result = applyAPriori(movies, ratTest)
    confMatrix = createConfusionMatrix(ratTest, result)
    printMatrix(confMatrix, sys.stdout)
    acRandom = accuracy(confMatrix)
    wAcRandom = weightedAccuracy(confMatrix)

   # Comparação dos classificadores
    kappa = (acTree - acRandom) / (1 - acRandom)
    wkappa = (wAcTree - wAcRandom) / (1 - wAcRandom)
    print("COMPARISON OF CLASSIFIERS")
    print("Tree:     accuracy = %.3f" % acTree)
    print(" weighted accuracy = %.3f" % wAcTree)
    print("A Priori: accuracy = %.3f" % acRandom)
    print(" weighted accuracy = %.3f" % wAcRandom)
    print("Kappa:               %.3f" % kappa)
    print("Weighted kappa:      %.3f" % wkappa)

    # RECOMENDAÇÃO DE FILMES
    print("Iniciando recomendações...")
    print("Digite sua profissão segundo a legenda:")
    for oc in occupations:
        print("{}: {}".format(oc, occupations[oc]))
    prof = int(input("> "))
    print("Digite sua idade segundo a legenda")
    for i in range(len(varage.domain)):
        if i < len(varage.domain) - 1:
            print("{0}-{1}: {0}".format(varage.domain[i], varage.domain[i+1]))
        else:
            print("{0}+:    {0}".format(varage.domain[i]))
    idade = int(input("> "))
    gen = ""
    while gen != "M" and gen != "F":
        print("Digite seu gênero (M/F)")
        gen = str(input("> "))
    user = Person(ratings[-1].userid + 1, gen, idade, prof)
    treeRecs = treeRecommend(decisionTree, user)
    print("Tree generated recommendations:")
    print("\t1. {}".format(treeRecs[0].name))
    print("\t2. {}".format(treeRecs[1].name))
    print("\t3. {}".format(treeRecs[2].name))

    prioriRecs = aPrioriRecommend()
    print("A priori generated recommendations:")
    print("\t1. {}".format(prioriRecs[0].name))
    print("\t2. {}".format(prioriRecs[1].name))
    print("\t3. {}".format(prioriRecs[2].name))