import Button from "./components/Button";
import HeaderBar from "./components/HeaderBar";

function App() {
  return (
    <div className="frame">
      <HeaderBar />
      
      <div className="frame__container">
        <div className="section">
          <div className="section__container">
            Lorem ipsum dolor sit amet consectetur, adipisicing elit. Maxime
            consequatur ad minus a cum, blanditiis deserunt nam veritatis earum
            provident atque, dolorum, amet sed. Ea nostrum laborum praesentium
            ratione quasi? Molestiae, pariatur nostrum? Atque, debitis numquam
            placeat fugit cum voluptatum, velit in necessitatibus maxime et
            eaque quam qui doloribus. Quos, reiciendis. Quasi error ex, enim
            aspernatur veniam consequuntur cumque unde! Reiciendis eaque
            voluptates, magni earum temporibus nostrum quasi accusantium odio a
            voluptatem incidunt quisquam assumenda soluta autem quod iste
            nesciunt unde suscipit exercitationem. Quidem ipsum dolorem,
            reiciendis enim sapiente nulla.
            <div className="button-group">
              <Button type="primary" />
              <Button type="secondary" />
            </div>
          </div>
        </div>

        <div className="section">
          <div className="section__container">
            Lorem ipsum dolor sit amet consectetur, adipisicing elit. Maxime
            consequatur ad minus a cum, blanditiis deserunt nam veritatis earum
            provident atque, dolorum, amet sed. Ea nostrum laborum praesentium
            ratione quasi? Molestiae, pariatur nostrum? Atque, debitis numquam
            placeat fugit cum voluptatum, velit in necessitatibus maxime et
            eaque quam qui doloribus. Quos, reiciendis. Quasi error ex, enim
            aspernatur veniam consequuntur cumque unde! Reiciendis eaque
            voluptates, magni earum temporibus nostrum quasi accusantium odio a
            voluptatem incidunt quisquam assumenda soluta autem quod iste
            nesciunt unde suscipit exercitationem. Quidem ipsum dolorem,
            reiciendis enim sapiente nulla.
            <div className="button-group">
              <Button type="primary" />
              <Button type="secondary" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
