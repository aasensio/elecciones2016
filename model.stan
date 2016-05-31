data {
  int<lower=0> NPartidos;
  int<lower=0> NSondeos;
  int<lower=0> NEmpresas;
  int<lower=0> NDates;
  int<lower=0> NDatesPre;
  int<lower=0> eleccionesIndex;
  real<lower=0> sondeos[NSondeos, NPartidos];
  int empresa[NSondeos];
  vector[NSondeos] sigmaSondeo;
  int date[NSondeos];
  vector<lower=0>[NPartidos] alpha;
}
parameters {
  real<lower=0> sigmaPre[NPartidos];
  real<lower=0> sigmaPost[NPartidos];
  simplex[NPartidos] theta[NDates];
  real house_free[NEmpresas-1,NPartidos];
}

transformed parameters {
  real house[NEmpresas,NPartidos];
  
  for (i in 1:NPartidos) {
    for(k in 1:(NEmpresas-1)) {
      house[k,i] <- house_free[k,i];
    }
    house[NEmpresas,i] <- -sum(house_free[:,i]);
  }
}

model {

#  for (i in 1:NDates) {
#    theta[i] ~ dirichlet(alpha);
#  }

  for (i in 1:NPartidos) sigmaPre[i] ~ inv_gamma(0.01,0.01);
  for (i in 1:NPartidos) sigmaPost[i] ~ inv_gamma(0.01,0.01);
#  sigmaExtra ~ inv_gamma(0.001, 0.001);

  theta[1] ~dirichlet(alpha);

  for (i in 2:NDatesPre) {
    theta[i] ~ normal(theta[i-1], sigmaPre);
  }
  for (i in NDatesPre+1:NDates) {
    theta[i] ~ normal(theta[i-1], sigmaPost);
  }

  for (i in 1:NPartidos) {
    for (j in 1:NEmpresas-1) {
      house_free[j,i] ~ normal(0, 0.05);
    }
  }

  for (i in 1:NSondeos) {
    for (j in 1:NPartidos) {
      if (empresa[i] == eleccionesIndex)        
        sondeos[i,j] ~ normal(theta[date[i],j], sigmaSondeo[i]);
      else
        sondeos[i,j] ~ normal(theta[date[i],j] + house[empresa[i],j], sigmaSondeo[i]);
    }
  }

}